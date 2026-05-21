from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework import generics
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth import login as auth_login
from .serializers import RegisterSerializer, UserSerializer, ProfileUpdateSerializer, AdminUserSerializer, FirstLoginCredentialsSerializer
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.utils import timezone
import secrets
import string

User = get_user_model()


def is_accounts_admin(user):
    """Администратор или владелец: доступ к списку/редактированию всех сотрудников."""
    if not user or not user.is_authenticated:
        return False
    if user.is_staff or user.is_superuser:
        return True
    return getattr(user, 'role', None) in ('administrator', 'owner')

class RegisterView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if not is_accounts_admin(request.user):
            return Response({"detail": "Регистрацию сотрудников выполняет только администратор"}, status=status.HTTP_403_FORBIDDEN)
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(request, username=username, password=password)
        if not user:
            return Response({"detail":"invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        # establish session
        auth_login(request, user)
        data = UserSerializer(user).data
        data["must_change_credentials"] = bool(getattr(user, "must_change_credentials", False))
        return Response(data)


class APILogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"detail":"logged out"})

class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def put(self, request):
        user = request.user
        serializer = ProfileUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(UserSerializer(user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterPageView(View):
    def get(self, request):
        return redirect('/accounts/login/')


class LoginPageView(View):
    def get(self, request):
        if request.user.is_authenticated:
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
        return render(request, 'accounts/login.html')


class ProfilePageView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('/accounts/login/?next=/accounts/profile/')
        from apps.schedule.constants import PVZ_ADDRESSES
        return render(request, 'accounts/profile.html', {'pvz_list': PVZ_ADDRESSES})


class FirstLoginPageView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('/accounts/login/?next=/accounts/first-login/')
        from apps.schedule.constants import PVZ_ADDRESSES
        return render(request, 'accounts/first_login.html', {'pvz_list': PVZ_ADDRESSES})


class EmployeesPageView(View):
    """Страница сотрудников — только для админа и владельца."""
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('/accounts/login/?next=/accounts/employees/')
        if not is_accounts_admin(request.user):
            return redirect('/')
        from apps.schedule.constants import PVZ_ADDRESSES
        return render(request, 'accounts/employees.html', {
            'pvz_list': PVZ_ADDRESSES,
            'current_user_id': request.user.id,
        })


class LogoutView(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect('/')


class UserListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_queryset(self):
        user = self.request.user
        if is_accounts_admin(user):
            return User.objects.all().order_by('username')
        return User.objects.filter(pvz_address=user.pvz_address).order_by('username')


class UserDetailView(APIView):
    """Просмотр и редактирование сотрудника (только для админа/владельца)."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        if not is_accounts_admin(request.user):
            return Response({"detail": "Нет доступа"}, status=status.HTTP_403_FORBIDDEN)
        try:
            user = User.objects.get(pk=pk)
            return Response(AdminUserSerializer(user).data)
        except User.DoesNotExist:
            return Response({"detail": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        if not is_accounts_admin(request.user):
            return Response({"detail": "Нет доступа"}, status=status.HTTP_403_FORBIDDEN)
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"detail": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)
        data = request.data.copy()
        # Нельзя уволить себя
        if request.user.id == user.id and data.get('is_active') is False:
            return Response({"detail": "Нельзя уволить себя"}, status=status.HTTP_400_BAD_REQUEST)
        # Пароль опционален при обновлении; если передан — меняем
        if not data.get('password'):
            data.pop('password', None)
        serializer = AdminUserSerializer(user, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(AdminUserSerializer(user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if not is_accounts_admin(request.user):
            return Response({"detail": "Нет доступа"}, status=status.HTTP_403_FORBIDDEN)
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"detail": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)
        if request.user.id == user.id:
            return Response({"detail": "Нельзя удалить свой аккаунт"}, status=status.HTTP_400_BAD_REQUEST)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserCreateByAdminView(APIView):
    """Создание сотрудника (только для админа/владельца)."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if not is_accounts_admin(request.user):
            return Response({"detail": "Нет доступа"}, status=status.HTTP_403_FORBIDDEN)
        serializer = AdminUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(AdminUserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BulkUserCreateByAdminView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if not is_accounts_admin(request.user):
            return Response({"detail": "Нет доступа"}, status=status.HTTP_403_FORBIDDEN)

        try:
            count = int(request.data.get("count", 0))
        except (ValueError, TypeError):
            count = 0
        if count <= 0 or count > 500:
            return Response({"detail": "Количество должно быть от 1 до 500"}, status=status.HTTP_400_BAD_REQUEST)

        alphabet = string.ascii_lowercase + string.digits
        created = []
        created_lines = ["Логин;Временный пароль"]
        stamp = timezone.now().strftime("%y%m%d%H%M")

        for idx in range(1, count + 1):
            while True:
                username = f"emp{stamp}{secrets.randbelow(9999):04d}"
                if not User.objects.filter(username=username).exists():
                    break
            temp_password = "".join(secrets.choice(alphabet) for _ in range(10))
            phone = f"+79{secrets.randbelow(10**9):09d}"
            while User.objects.filter(phone_number=phone).exists():
                phone = f"+79{secrets.randbelow(10**9):09d}"
            user = User(
                username=username,
                first_name="-",
                last_name="-",
                email="-",
                phone_number=phone,
                pvz_address="-",
                role="staff_manager",
                must_change_credentials=True,
            )
            user.set_password(temp_password)
            user.save()
            created.append(user)
            created_lines.append(f"{username};{temp_password}")

        content = "\n".join(created_lines)
        response = HttpResponse(content, content_type="text/plain; charset=utf-8")
        response["Content-Disposition"] = f'attachment; filename="bulk_accounts_{stamp}.txt"'
        return response


class FirstLoginCredentialsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if not getattr(request.user, "must_change_credentials", False):
            return Response({"detail": "Смена учётных данных не требуется"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = FirstLoginCredentialsSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        current_password = serializer.validated_data["current_password"]
        if not request.user.check_password(current_password):
            return Response({"detail": "Текущий пароль введён неверно"}, status=status.HTTP_400_BAD_REQUEST)

        request.user.username = serializer.validated_data["new_username"]
        request.user.set_password(serializer.validated_data["new_password"])
        pvz = (serializer.validated_data.get("pvz_address") or "").strip()
        if pvz:
            request.user.pvz_address = pvz
        request.user.must_change_credentials = False
        request.user.save()
        auth_login(request, request.user)
        return Response(UserSerializer(request.user).data)
