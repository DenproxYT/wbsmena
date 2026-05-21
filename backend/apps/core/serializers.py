from rest_framework import serializers
from .models import SiteAnnouncement, UserNotification, Feedback


class UserNotificationSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='announcement.title', read_only=True)
    message = serializers.CharField(source='announcement.message', read_only=True)
    created_at = serializers.DateTimeField(source='announcement.created_at', read_only=True)
    is_read = serializers.BooleanField(read_only=True)

    class Meta:
        model = UserNotification
        fields = ['id', 'title', 'message', 'created_at', 'read_at', 'is_read']


class AnnouncementCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    message = serializers.CharField()


class FeedbackSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    full_name = serializers.SerializerMethodField()
    attachment = serializers.SerializerMethodField()

    class Meta:
        model = Feedback
        fields = [
            'id', 'category', 'category_display', 'comment', 'attachment',
            'status', 'created_at', 'username', 'full_name',
        ]
        read_only_fields = ['status', 'created_at']

    def get_full_name(self, obj):
        return f'{obj.user.last_name} {obj.user.first_name}'.strip() or obj.user.username

    def get_attachment(self, obj):
        if obj.attachment:
            return obj.attachment.url
        return None


class FeedbackCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['category', 'comment', 'attachment']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
