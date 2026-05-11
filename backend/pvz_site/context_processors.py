def accounts_admin(request):
    """Доступ к разделу «Сотрудники» только для админа и владельца."""
    try:
        if not getattr(request, 'user', None) or not getattr(request.user, 'is_authenticated', False):
            return {'is_accounts_admin': False}
        user = request.user
        is_admin = getattr(user, 'is_staff', False) or getattr(user, 'is_superuser', False) or getattr(user, 'role', None) in ('administrator', 'owner')
        return {'is_accounts_admin': bool(is_admin)}
    except Exception:
        return {'is_accounts_admin': False}
