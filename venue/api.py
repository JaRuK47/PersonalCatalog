from rest_framework import viewsets
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Avg, Max, Min, Q
from django.utils import timezone
from datetime import timedelta

from django.contrib.auth.models import User
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.contrib.auth import authenticate

from .models import Venue, Session, Booking, Round, RoundPlayer, GameMode
from .serializers import (
    VenueSerializer, SessionSerializer, BookingSerializer,
    RoundSerializer, RoundPlayerSerializer, UserSerializer, GameModeSerializer,
    VenueStatsSerializer, BookingStatsSerializer, SessionStatsSerializer, RoundStatsSerializer, RoundPlayerStatsSerializer
)

class GameModeViewSet(viewsets.ModelViewSet):
    queryset = GameMode.objects.all()
    serializer_class = GameModeSerializer

class ProfileViewSet(GenericViewSet):
    queryset = User.objects.all()

    @action(detail=False, url_path="me", methods=['GET'])
    def get_me(self, request, *args, **kwargs):
        data = {'is_authenticated': self.request.user.is_authenticated}
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

    @action(detail=False, methods=['GET'], url_path='stats')
    def get_stats(self, request):
        stats = self.get_queryset().aggregate(
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

    def get_queryset(self):
        qs = super().get_queryset().order_by('-date', '-start_time')
        venue_id = self.request.query_params.get('venue')
        if venue_id:
            qs = qs.filter(venue_id=venue_id)
        mode_id = self.request.query_params.get('game_mode')
        if mode_id:
            qs = qs.filter(game_mode_id=mode_id)
        status_param = self.request.query_params.get('status')
        if status_param == 'cancelled':
            qs = qs.filter(is_cancelled=True)
        elif status_param == 'active':
            qs = qs.filter(is_cancelled=False)
        return qs

    @action(detail=False, methods=['GET'], url_path='stats')
    def get_stats(self, request):
        stats = self.get_queryset().aggregate(
            count=Count('id'),
            cancelled_count=Count('id', filter=Q(is_cancelled=True))
        )
        serializer = SessionStatsSerializer(instance=stats)
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
            pass
        else:
            qs = qs.filter(user=user)

        target_user = self.request.query_params.get('user')
        if target_user:
            qs = qs.filter(user_id=target_user)

        status_param = self.request.query_params.get('status')
        if status_param:
            if status_param == 'attended':
                threshold = timezone.now() - timedelta(hours=5)
                qs = qs.filter(
                    Q(status='attended') |
                    (
                            Q(status='active') & (
                            Q(session__date__lt=threshold.date()) |
                            (Q(session__date=threshold.date()) & Q(session__start_time__lt=threshold.time()))
                    )
                    )
                )
            elif status_param == 'active':
                threshold = timezone.now() - timedelta(hours=5)
                qs = qs.filter(
                    Q(status='active') & (
                            Q(session__date__gt=threshold.date()) |
                            (Q(session__date=threshold.date()) & Q(session__start_time__gte=threshold.time()))
                    )
                )
            else:
                qs = qs.filter(status=status_param)

        session_param = self.request.query_params.get('session')
        if session_param:
            qs = qs.filter(session_id=session_param)

        return qs

    @action(detail=False, methods=['GET'], url_path='stats')
    def get_stats(self, request):
        qs = self.get_queryset()
        threshold = timezone.now() - timedelta(hours=5)

        count = qs.count()
        active_count = qs.filter(
            Q(status='active') & (
                    Q(session__date__gt=threshold.date()) |
                    (Q(session__date=threshold.date()) & Q(session__start_time__gte=threshold.time()))
            )
        ).count()
        no_show_count = qs.filter(status='no_show').count()

        stats = {
            "count": count,
            "active_count": active_count,
            "no_show_count": no_show_count
        }
        serializer = BookingStatsSerializer(instance=stats)
        return Response(serializer.data)

class RoundViewSet(viewsets.ModelViewSet):
    queryset = Round.objects.all()
    serializer_class = RoundSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        session_id = self.request.query_params.get('session')
        if session_id:
            qs = qs.filter(session_id=session_id)
        host_id = self.request.query_params.get('host')
        if host_id:
            qs = qs.filter(host_id=host_id)
        mode_id = self.request.query_params.get('game_mode')
        if mode_id:
            qs = qs.filter(game_mode_id=mode_id)
        return qs

    @action(detail=False, methods=['GET'], url_path='stats')
    def get_stats(self, request):
        stats = self.get_queryset().aggregate(
            count=Count('id'),
            mafia_wins=Count('id', filter=Q(winning_team='mafia')),
            town_wins=Count('id', filter=Q(winning_team='town'))
        )
        serializer = RoundStatsSerializer(instance=stats)
        return Response(serializer.data)

class RoundPlayerViewSet(viewsets.ModelViewSet):
    queryset = RoundPlayer.objects.all()
    serializer_class = RoundPlayerSerializer

    @action(detail=False, methods=['GET'], url_path='stats')
    def get_stats(self, request):
        stats = self.get_queryset().aggregate(
            count=Count('id'),
            avg_points=Avg('points'),
            max_points=Max('points'),
            min_points=Min('points')
        )
        if stats['count'] == 0:
            return Response({"count": 0, "avg_points": 0, "max_points": 0, "min_points": 0})
        serializer = RoundPlayerStatsSerializer(instance=stats)
        return Response(serializer.data)