from django.shortcuts import render, redirect
from django.urls import reverse


def index(request):
  if not request.user.is_authenticated:
    return redirect(f'/accounts/login/?next={request.path or "/"}')
  links = [
    { 'title': 'График работы', 'url': '/schedule/', 'desc': 'Управление сменами и календарь сотрудников' },
    { 'title': 'Обучение', 'url': '/training/', 'desc': 'Материалы и тесты для сотрудников' },
  ]
  if request.user.is_authenticated:
    links.append({ 'title': 'Профиль', 'url': '/accounts/profile/', 'desc': 'Ваша учётная запись и настройки' })
  is_admin = request.user.is_authenticated and (
    request.user.is_staff or request.user.is_superuser or getattr(request.user, 'role', None) in ('administrator', 'owner')
  )
  if request.user.is_authenticated and request.user.is_staff:
    links.insert(0, { 'title': 'Панель администратора', 'url': reverse('admin:index'), 'desc': 'Управление пользователями и данными' })
  if is_admin:
    links.append({ 'title': 'Сотрудники', 'url': '/accounts/employees/', 'desc': 'Список сотрудников, роли и учётные записи' })
  return render(request, 'root.html', { 'links': links })
