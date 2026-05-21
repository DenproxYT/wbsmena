from datetime import date
from calendar import monthrange

from django.utils import timezone

from .models import SchedulePeriod


def month_key(year: int, month: int) -> tuple[int, int]:
    return year, month


def current_month_today() -> date:
    return timezone.localdate()


def add_months(d: date, months: int) -> date:
    y = d.year + (d.month - 1 + months) // 12
    m = (d.month - 1 + months) % 12 + 1
    return date(y, m, 1)


def ensure_period(year: int, month: int) -> SchedulePeriod:
    """Создаёт период при отсутствии; следующий месяц по умолчанию закрыт."""
    today = current_month_today()
    cur_y, cur_m = today.year, today.month
    next_d = add_months(today, 1)
    next_y, next_m = next_d.year, next_d.month

    period, created = SchedulePeriod.objects.get_or_create(
        year=year,
        month=month,
        defaults={'is_open': False},
    )
    if created:
        if (year, month) == (cur_y, cur_m):
            period.is_open = True
            period.save(update_fields=['is_open'])
        elif (year, month) == (next_y, next_m):
            period.is_open = False
            period.save(update_fields=['is_open'])
    return period


def get_visible_months_for_user(user, is_admin: bool) -> list[dict]:
    """Список месяцев для выпадающего списка графика."""
    today = current_month_today()
    cur = date(today.year, today.month, 1)
    nxt = add_months(today, 1)

    ensure_period(cur.year, cur.month)
    ensure_period(nxt.year, nxt.month)

    if is_admin:
        from .models import Schedule
        for d in Schedule.objects.dates('date', 'month', order='DESC'):
            ensure_period(d.year, d.month)
        periods = SchedulePeriod.objects.all().order_by('-year', '-month')
        seen = set()
        result = []
        for p in periods:
            key = (p.year, p.month)
            if key in seen:
                continue
            seen.add(key)
            result.append(_period_dict(p))
        if not any((r['year'], r['month']) == (cur.year, cur.month) for r in result):
            result.insert(0, _period_dict(ensure_period(cur.year, cur.month)))
        return result

    months = [
        _period_dict(ensure_period(cur.year, cur.month)),
        _period_dict(ensure_period(nxt.year, nxt.month)),
    ]
    return months


def _period_dict(period: SchedulePeriod) -> dict:
    return {
        'year': period.year,
        'month': period.month,
        'value': f'{period.year}-{period.month:02d}',
        'label': _month_label(period.year, period.month),
        'is_open': period.is_open,
    }


def month_label(year: int, month: int) -> str:
    return _month_label(year, month)


def _month_label(year: int, month: int) -> str:
    names = [
        'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
        'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь',
    ]
    return f'{names[month - 1]} {year}'


def is_period_open_for_editing(year: int, month: int, is_admin: bool) -> bool:
    if is_admin:
        return True
    period = ensure_period(year, month)
    return period.is_open


def is_date_in_allowed_range(d: date, is_admin: bool) -> bool:
    today = current_month_today()
    cur_start = date(today.year, today.month, 1)
    next_start = add_months(today, 1)
    next_end = date(
        next_start.year,
        next_start.month,
        monthrange(next_start.year, next_start.month)[1],
    )
    if is_admin:
        return True
    return cur_start <= d <= next_end


def check_schedule_write_allowed(user, schedule_date, is_admin: bool):
    """Возвращает (ok, error_message)."""
    if not is_date_in_allowed_range(schedule_date, is_admin):
        return False, 'Можно редактировать только текущий и следующий месяц'
    if not is_period_open_for_editing(
        schedule_date.year, schedule_date.month, is_admin
    ):
        return False, 'Проставление смен для этого месяца закрыто администратором'
    return True, None
