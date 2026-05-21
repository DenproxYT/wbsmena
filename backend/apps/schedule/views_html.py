from django.views import View
from django.shortcuts import render, redirect

from apps.accounts.views import is_accounts_admin
from .constants import PVZ_ADDRESSES
from .household_constants import HOUSEHOLD_SUPPLY_ITEMS
from .views import is_schedule_admin


class SchedulePageView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect(f'/accounts/login/?next=/schedule/')
        user = request.user
        items = [i for i in HOUSEHOLD_SUPPLY_ITEMS if i]
        return render(request, 'schedule/list.html', {
            'pvz_list': PVZ_ADDRESSES,
            'household_items': items,
            'is_schedule_admin': is_schedule_admin(user) if user.is_authenticated else False,
            'user_pvz_address': getattr(user, 'pvz_address', '') or '',
        })


class HouseholdRequestsAdminPageView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('/accounts/login/?next=/schedule/household-requests/')
        if not is_accounts_admin(request.user):
            return redirect('/schedule/')
        return render(request, 'schedule/household_admin.html')
