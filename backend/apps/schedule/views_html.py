from django.views import View
from django.shortcuts import render, redirect

from .constants import PVZ_ADDRESSES
from .views import is_schedule_admin


class SchedulePageView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect(f'/accounts/login/?next=/schedule/')
        user = request.user
        return render(request, 'schedule/list.html', {
            'pvz_list': PVZ_ADDRESSES,
            'is_schedule_admin': is_schedule_admin(user) if user.is_authenticated else False,
            'user_pvz_address': getattr(user, 'pvz_address', '') or '',
        })
