from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email", "phone_number", "pvz_address", "is_intern", "role", "role_display", "is_active"]


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """Только поля, которые пользователь может менять в своём профиле."""
    role = serializers.ChoiceField(choices=[
        ("intern", "Стажёр"),
        ("staff_manager", "Штатный менеджер"),
        ("chief_manager", "Главный менеджер"),
    ], required=False)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone_number", "pvz_address", "role"]


class AdminUserSerializer(serializers.ModelSerializer):
    """Для админа/владельца: полное редактирование сотрудника."""
    password = serializers.CharField(write_only=True, required=False)
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email", "phone_number", "pvz_address", "is_intern", "role", "role_display", "password", "is_active", "must_change_credentials"]

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        if not password:
            raise serializers.ValidationError({"password": "Обязательное поле"})
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "password", "first_name", "last_name", "phone_number", "pvz_address", "is_intern"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class FirstLoginCredentialsSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_username = serializers.CharField(max_length=150)
    new_password = serializers.CharField(write_only=True, min_length=6)
    pvz_address = serializers.CharField(max_length=255, required=False, allow_blank=True)

    def validate_pvz_address(self, value):
        from apps.schedule.constants import PVZ_ADDRESSES
        value = (value or '').strip()
        if value and value not in PVZ_ADDRESSES:
            raise serializers.ValidationError('Выберите ПВЗ из списка')
        return value

    def validate_new_username(self, value):
        user = self.context["request"].user
        exists = User.objects.filter(username=value).exclude(id=user.id).exists()
        if exists:
            raise serializers.ValidationError("Такой логин уже занят")
        return value
