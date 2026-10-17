from rest_framework import viewsets

from .models import Venue, Session, Booking, Round, RoundPlayer
from .serializers import (
    VenueSerializer,
    SessionSerializer,
    BookingSerializer,
    RoundSerializer,
    RoundPlayerSerializer,
)
from django.contrib.auth.models import User
from .serializers import UserSerializer

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class VenueViewSet(viewsets.ModelViewSet):
    queryset = Venue.objects.all()
    serializer_class = VenueSerializer


class SessionViewSet(viewsets.ModelViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer


class RoundViewSet(viewsets.ModelViewSet):
    queryset = Round.objects.all()
    serializer_class = RoundSerializer


class RoundPlayerViewSet(viewsets.ModelViewSet):
    queryset = RoundPlayer.objects.all()
    serializer_class = RoundPlayerSerializer