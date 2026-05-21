from django.views import View
from django.shortcuts import render, redirect

from apps.accounts.views import is_accounts_admin
from apps.schedule.constants import PVZ_ADDRESSES


class FeedbackPageView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('/accounts/login/?next=/feedback/')
        return render(request, 'core/feedback.html')


class FeedbackAdminPageView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('/accounts/login/?next=/feedback/admin/')
        if not is_accounts_admin(request.user):
            return redirect('/feedback/')
        return render(request, 'core/feedback_admin.html')


class NotificationsAdminPageView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('/accounts/login/?next=/notifications/send/')
        if not is_accounts_admin(request.user):
            return redirect('/')
        return render(request, 'core/notifications_send.html', {
            'pvz_list': PVZ_ADDRESSES,
        })
