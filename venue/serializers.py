from rest_framework import serializers
from django.contrib.auth.models import User
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
    status = serializers.ReadOnlyField()
    booked_users = serializers.SerializerMethodField()

    class Meta:
        model = Session
        exclude = ['db_status']

    def get_booked_users(self, obj):
        bookings = obj.bookings.filter(status__in=['active', 'attended'])
        return [b.user.username for b in bookings]

class BookingSerializer(serializers.ModelSerializer):
    status_display = serializers.ReadOnlyField()
    user_name = serializers.ReadOnlyField()

    class Meta:
        model = Booking
        fields = '__all__'

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