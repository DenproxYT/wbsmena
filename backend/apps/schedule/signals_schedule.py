from datetime import date as date_type

from apps.core.realtime import publish_all


def emit_schedule_changed(schedule_date) -> None:
    if isinstance(schedule_date, str):
        schedule_date = date_type.fromisoformat(schedule_date[:10])
    publish_all(
        'schedule_changed',
        {'year': schedule_date.year, 'month': schedule_date.month},
    )
