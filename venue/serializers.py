from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta, time
from .models import Venue, Session, Booking, Round, RoundPlayer


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

    class Meta:
        model = Session
        fields = '__all__'

    def get_status(self, obj):
        if not obj.date or not obj.start_time: return "Идёт набор"
        start = timezone.make_aware(datetime.combine(obj.date, obj.start_time), timezone.get_current_timezone())
        now = timezone.now()
        if now < start:
            return "Идёт набор"
        elif start <= now < start + timedelta(hours=5):
            return "Активно"
        else:
            return "Завершена"


class BookingSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = '__all__'

    def get_status(self, obj):
        if obj.status == 'cancelled':
            return "Отменено"
        if obj.status == 'no_show':
            return "Неявка"

        if not obj.session.date or not obj.session.start_time:
            return "Ожидание"

        end_time = timezone.make_aware(datetime.combine(obj.session.date, obj.session.start_time),
                                       timezone.get_current_timezone()) + timedelta(hours=5)
        now = timezone.now()

        if now > end_time:
            return "Явился"
        return "Активно"


class RoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Round
        fields = '__all__'


class RoundPlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoundPlayer
        fields = '__all__'