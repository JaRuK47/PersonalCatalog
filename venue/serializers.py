from rest_framework import serializers
from .models import Venue, Session, Booking, Round, RoundPlayer


class VenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue
        fields = '__all__'


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = '__all__'


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'


class RoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Round
        fields = '__all__'


class RoundPlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoundPlayer
        fields = '__all__'