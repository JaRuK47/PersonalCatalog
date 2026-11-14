from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta, time
from .models import Venue, Session, Booking, Round, RoundPlayer, GameMode

class GameModeSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameMode
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class VenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue
        fields = '__all__'


class SessionSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    booked_users = serializers.SerializerMethodField()

    class Meta:
        model = Session
        fields = '__all__'

    def get_status(self, obj):
        if obj.is_cancelled: return "Отменена"
        if not obj.date or not obj.start_time: return "Идёт набор"
        start = timezone.make_aware(datetime.combine(obj.date, obj.start_time), timezone.get_current_timezone())
        now = timezone.now()
        if now < start:
            return "Идёт набор"
        elif start <= now < start + timedelta(hours=5):
            return "Активно"
        else:
            return "Завершена"

    def get_booked_users(self, obj):
        bookings = obj.bookings.filter(status__in=['active', 'attended'])
        return [b.user.username for b in bookings]

class BookingSerializer(serializers.ModelSerializer):
    status_display = serializers.SerializerMethodField()
    user_name = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Booking
        fields = '__all__'

    def get_status_display(self, obj):
        if obj.status == 'cancelled': return "Отменено"
        if obj.status == 'no_show': return "Неявка"
        if not obj.session.date or not obj.session.start_time: return "Ожидание"
        end_time = timezone.make_aware(datetime.combine(obj.session.date, obj.session.start_time),
                                       timezone.get_current_timezone()) + timedelta(hours=5)
        if timezone.now() > end_time: return "Явился"
        return "Активно"

    def create(self, validated_data):
        user = self.context['request'].user
        if user.is_authenticated:
            if hasattr(user, 'profile') and user.profile.role in [2, 3]:
                pass
            else:
                validated_data['user'] = user

        return super().create(validated_data)


class RoundPlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoundPlayer
        fields = '__all__'

    def create(self, validated_data):
        return super().create(validated_data)


class RoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Round
        fields = '__all__'

class VenueStatsSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    avg_capacity = serializers.FloatField()
    max_capacity = serializers.IntegerField()
    min_capacity = serializers.IntegerField()

class BookingStatsSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    active_count = serializers.IntegerField()
    no_show_count = serializers.IntegerField()

class RoundPlayerStatsSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    avg_points = serializers.FloatField()
    max_points = serializers.FloatField()
    min_points = serializers.FloatField()

class SessionStatsSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    cancelled_count = serializers.IntegerField()

class RoundStatsSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    mafia_wins = serializers.IntegerField()
    town_wins = serializers.IntegerField()