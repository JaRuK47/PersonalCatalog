from rest_framework import viewsets
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response

from django.contrib.auth.models import User
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.contrib.auth import authenticate

from .models import Venue, Session, Booking, Round, RoundPlayer
from .serializers import (
    VenueSerializer, SessionSerializer, BookingSerializer,
    RoundSerializer, RoundPlayerSerializer, UserSerializer
)

class ProfileViewSet(GenericViewSet):
    queryset = User.objects.all()

    @action(detail=False, url_path="me", methods=['GET'])
    def get_me(self, request, *args, **kwargs):
        data = {
            'is_authenticated': self.request.user.is_authenticated
        }
        if self.request.user.is_authenticated:
            role_display = self.request.user.profile.get_role_display() if hasattr(self.request.user, 'profile') else None
            data.update({
                "username": self.request.user.username,
                "id": self.request.user.id,
                "role": role_display,
            })
        return Response(data=data)

    @action(detail=False, url_path="login", methods=['POST'])
    def login(self, *args, **kwargs):
        username = self.request.data.get('username')
        password = self.request.data.get('password')

        user = authenticate(username=username, password=password)
        if user:
            django_login(self.request, user)
            return Response({'success': True}, status=200)

        return Response({'success': False}, status=403)

    @action(detail=False, url_path="logout", methods=['POST'])
    def logout(self, *args, **kwargs):
        django_logout(self.request)
        return Response(status=200)
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