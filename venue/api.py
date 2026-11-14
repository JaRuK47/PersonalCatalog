from rest_framework import viewsets
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Avg, Max, Min, Q

from django.contrib.auth.models import User
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.contrib.auth import authenticate
from .models import Venue, Session, Booking, Round, RoundPlayer, GameMode
from .serializers import (
    VenueSerializer, SessionSerializer, BookingSerializer,
    RoundSerializer, RoundPlayerSerializer, UserSerializer, GameModeSerializer,
    VenueStatsSerializer, BookingStatsSerializer, RoundPlayerStatsSerializer,
    SessionStatsSerializer,  RoundStatsSerializer
)

class VenueViewSet(viewsets.ModelViewSet):
    queryset = Venue.objects.all()
    serializer_class = VenueSerializer

    @action(detail=False, methods=['GET'], url_path='stats')
    def get_stats(self, request):
        stats = Venue.objects.aggregate(
            count=Count('id'),
            avg_capacity=Avg('capacity'),
            max_capacity=Max('capacity'),
            min_capacity=Min('capacity')
        )
        if stats['count'] == 0:
            return Response({"count": 0, "avg_capacity": 0, "max_capacity": 0, "min_capacity": 0})

        serializer = VenueStatsSerializer(instance=stats)
        return Response(serializer.data)


class SessionViewSet(viewsets.ModelViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer

    @action(detail=False, methods=['GET'], url_path='stats')
    def get_stats(self, request):
        stats = Session.objects.aggregate(
            count=Count('id'),
            cancelled_count=Count('id', filter=Q(is_cancelled=True))
        )
        serializer = SessionStatsSerializer(instance=stats)
        return Response(serializer.data)


class RoundViewSet(viewsets.ModelViewSet):
    queryset = Round.objects.all()
    serializer_class = RoundSerializer

    @action(detail=False, methods=['GET'], url_path='stats')
    def get_stats(self, request):
        stats = Round.objects.aggregate(
            count=Count('id'),
            mafia_wins=Count('id', filter=Q(winning_team='mafia')),
            town_wins=Count('id', filter=Q(winning_team='town'))
        )
        serializer = RoundStatsSerializer(instance=stats)
        return Response(serializer.data)


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def get_queryset(self):
        qs = super().get_queryset().order_by('-created_at')
        user = self.request.user
        if not user.is_authenticated:
            return qs.none()
        if user.is_superuser or (hasattr(user, 'profile') and user.profile.role in [2, 3]):
            target_user = self.request.query_params.get('user')
            if target_user:
                return qs.filter(user_id=target_user)
            return qs
        return qs.filter(user=user)

    @action(detail=False, methods=['GET'], url_path='stats')
    def get_stats(self, request):
        qs = self.get_queryset()
        stats = qs.aggregate(
            count=Count('id'),
            active_count=Count('id', filter=Q(status='active')),
            no_show_count=Count('id', filter=Q(status='no_show'))
        )
        serializer = BookingStatsSerializer(instance=stats)
        return Response(serializer.data)


class RoundPlayerViewSet(viewsets.ModelViewSet):
    queryset = RoundPlayer.objects.all()
    serializer_class = RoundPlayerSerializer

    @action(detail=False, methods=['GET'], url_path='stats')
    def get_stats(self, request):
        stats = RoundPlayer.objects.aggregate(
            count=Count('id'),
            avg_points=Avg('points'),
            max_points=Max('points'),
            min_points=Min('points')
        )
        if stats['count'] == 0:
            return Response({"count": 0, "avg_points": 0, "max_points": 0, "min_points": 0})

        serializer = RoundPlayerStatsSerializer(instance=stats)
        return Response(serializer.data)

class GameModeViewSet(viewsets.ModelViewSet):
    queryset = GameMode.objects.all()
    serializer_class = GameModeSerializer

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