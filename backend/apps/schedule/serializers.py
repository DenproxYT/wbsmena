from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Schedule, HouseholdSupplyRequest
from .household_constants import HOUSEHOLD_SUPPLY_ITEMS

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


class HouseholdSupplyRequestSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = HouseholdSupplyRequest
        fields = [
            'id', 'username', 'pvz_address',
            'item_1', 'item_2', 'item_3', 'item_4', 'item_5',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at', 'username']

    def validate_pvz_address(self, value):
        from .constants import PVZ_ADDRESSES
        if value not in PVZ_ADDRESSES:
            raise serializers.ValidationError('Выберите ПВЗ из списка')
        return value

    def _validate_item(self, value):
        if value and value not in HOUSEHOLD_SUPPLY_ITEMS:
            raise serializers.ValidationError('Недопустимая позиция')
        return value or ''

    def validate_item_1(self, value):
        return self._validate_item(value)

    def validate_item_2(self, value):
        return self._validate_item(value)

    def validate_item_3(self, value):
        return self._validate_item(value)

    def validate_item_4(self, value):
        return self._validate_item(value)

    def validate_item_5(self, value):
        return self._validate_item(value)

    def validate(self, attrs):
        items = [attrs.get(f'item_{i}', '') for i in range(1, 6)]
        if not any(items):
            raise serializers.ValidationError('Выберите хотя бы одну позицию')
        return attrs

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
