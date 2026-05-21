from django.contrib import admin

from .models import Feedback, SiteAnnouncement, UserNotification


@admin.register(SiteAnnouncement)
class SiteAnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'created_at')
    search_fields = ('title', 'message')
    readonly_fields = ('created_at',)


@admin.register(UserNotification)
class UserNotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'announcement', 'read_at')
    list_filter = ('read_at',)
    search_fields = ('user__username', 'announcement__title')
    raw_id_fields = ('user', 'announcement')


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'status', 'created_at')
    list_filter = ('category', 'status')
    search_fields = ('user__username', 'comment')
    readonly_fields = ('created_at',)
