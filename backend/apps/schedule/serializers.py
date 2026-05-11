from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Schedule

User = get_user_model()


class ScheduleSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    full_name = serializers.SerializerMethodField(read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, allow_null=True, default=serializers.CurrentUserDefault())
    pvz_address = serializers.CharField(required=False, allow_blank=True)

    def get_full_name(self, obj):
        if obj.user:
            name = f"{obj.user.first_name or ''} {obj.user.last_name or ''}".strip()
            return name or obj.user.username
        return ''
    
    class Meta:
        model = Schedule
        fields = ["id", "user", "user_id", "username", "full_name", "date", "shifts", "comment", "pvz_address"]
        read_only_fields = ("username", "full_name", "user_id")
