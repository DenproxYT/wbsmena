from django.contrib import admin

from .models import HouseholdSupplyRequest, Schedule, SchedulePeriod


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('date', 'user', 'shifts', 'pvz_address')
    list_filter = ('date', 'pvz_address')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'pvz_address')
    date_hierarchy = 'date'
    raw_id_fields = ('user',)


@admin.register(SchedulePeriod)
class SchedulePeriodAdmin(admin.ModelAdmin):
    list_display = ('year', 'month', 'is_open', 'updated_at', 'updated_by')
    list_filter = ('is_open', 'year')
    ordering = ('-year', '-month')


@admin.register(HouseholdSupplyRequest)
class HouseholdSupplyRequestAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'user', 'pvz_address')
    list_filter = ('pvz_address', 'created_at')
    search_fields = ('user__username', 'pvz_address')
    readonly_fields = ('created_at',)
