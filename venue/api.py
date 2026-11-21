from rest_framework import viewsets
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Avg, Max, Min, Q
from django.utils import timezone
from datetime import timedelta
from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.utils import get_column_letter

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

def generate_excel_response(headers, data, filename):
    wb = Workbook()
    ws = wb.active
    ws.append(headers)
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.font = cell.font.copy(bold=True)
        ws.column_dimensions[get_column_letter(col_num)].width = 20
    for row in data:
        ws.append(row)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{filename}.xlsx"'
    wb.save(response)
    return response

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
            data.update({"username": self.request.user.username, "id": self.request.user.id, "role": role_display})
        return Response(data=data)

    @action(detail=False, url_path="login", methods=['POST'])
    def login(self, *args, **kwargs):
        user = authenticate(username=self.request.data.get('username'), password=self.request.data.get('password'))
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
        stats = self.get_queryset().aggregate(count=Count('id'), avg_capacity=Avg('capacity'), max_capacity=Max('capacity'), min_capacity=Min('capacity'))
        if stats['count'] == 0: return Response({"count": 0, "avg_capacity": 0, "max_capacity": 0, "min_capacity": 0})
        return Response(VenueStatsSerializer(instance=stats).data)

    @action(detail=False, methods=['GET'], url_path='export')
    def export_excel(self, request):
        qs = self.get_queryset()
        headers = ['ID', 'Название', 'Адрес', 'Вместимость', 'Описание']
        data = [[v.id, v.name, v.address, v.capacity, v.description] for v in qs]
        return generate_excel_response(headers, data, 'venues_export')

class SessionViewSet(viewsets.ModelViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer

    def get_queryset(self):
        qs = super().get_queryset().order_by('-date', '-start_time')
        if venue_id := self.request.query_params.get('venue'): qs = qs.filter(venue_id=venue_id)
        if mode_id := self.request.query_params.get('game_mode'): qs = qs.filter(game_mode_id=mode_id)
        status_param = self.request.query_params.get('status')
        if status_param:
            now = timezone.localtime(timezone.now())
            threshold = now - timedelta(hours=5)
            if status_param == 'cancelled': qs = qs.filter(is_cancelled=True)
            else:
                qs = qs.filter(is_cancelled=False)
                if status_param == 'upcoming': qs = qs.filter(Q(date__gt=now.date()) | (Q(date=now.date()) & Q(start_time__gt=now.time())))
                elif status_param == 'finished': qs = qs.filter(Q(date__lt=threshold.date()) | (Q(date=threshold.date()) & Q(start_time__lte=threshold.time())))
                elif status_param == 'active':
                    qs = qs.filter((Q(date__gt=threshold.date()) | (Q(date=threshold.date()) & Q(start_time__gt=threshold.time()))) & (Q(date__lt=now.date()) | (Q(date=now.date()) & Q(start_time__lte=now.time()))))
        return qs

    @action(detail=False, methods=['GET'], url_path='stats')
    def get_stats(self, request):
        stats = self.get_queryset().aggregate(count=Count('id'), cancelled_count=Count('id', filter=Q(is_cancelled=True)))
        return Response(SessionStatsSerializer(instance=stats).data)

    @action(detail=False, methods=['GET'], url_path='export')
    def export_excel(self, request):
        qs = self.get_queryset()
        headers = ['ID', 'Дата', 'Время', 'Игра', 'Режим', 'Локация', 'Статус', 'Макс. игроков']
        data = [[s.id, s.date.strftime('%d.%m.%Y') if s.date else '', s.start_time.strftime('%H:%M') if s.start_time else '', s.title, s.game_mode.name if s.game_mode else '—', s.venue.name if s.venue else '—', s.status, s.max_players] for s in qs]
        return generate_excel_response(headers, data, 'sessions_export')

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def get_queryset(self):
        qs = super().get_queryset().order_by('-created_at')
        user = self.request.user
        if not user.is_authenticated: return qs.none()
        if user.is_superuser or (hasattr(user, 'profile') and user.profile.role in [2, 3]): pass
        else: qs = qs.filter(user=user)

        if target_user := self.request.query_params.get('user'): qs = qs.filter(user_id=target_user)
        status_param = self.request.query_params.get('status')
        if status_param:
            if status_param == 'attended':
                threshold = timezone.now() - timedelta(hours=5)
                qs = qs.filter(Q(status='attended') | (Q(status='active') & (Q(session__date__lt=threshold.date()) | (Q(session__date=threshold.date()) & Q(session__start_time__lt=threshold.time())))))
            elif status_param == 'active':
                threshold = timezone.now() - timedelta(hours=5)
                qs = qs.filter(Q(status='active') & (Q(session__date__gt=threshold.date()) | (Q(session__date=threshold.date()) & Q(session__start_time__gte=threshold.time()))))
            else: qs = qs.filter(status=status_param)
        if session_param := self.request.query_params.get('session'): qs = qs.filter(session_id=session_param)
        return qs

    @action(detail=False, methods=['GET'], url_path='stats')
    def get_stats(self, request):
        qs = self.get_queryset()
        threshold = timezone.now() - timedelta(hours=5)
        stats = {
            "count": qs.count(),
            "active_count": qs.filter(Q(status='active') & (Q(session__date__gt=threshold.date()) | (Q(session__date=threshold.date()) & Q(session__start_time__gte=threshold.time())))).count(),
            "no_show_count": qs.filter(status='no_show').count()
        }
        return Response(BookingStatsSerializer(instance=stats).data)

    @action(detail=False, methods=['GET'], url_path='export')
    def export_excel(self, request):
        qs = self.get_queryset()
        headers = ['ID', 'Пользователь', 'Игра', 'Дата игры', 'Время ухода', 'Статус']
        data = [[b.id, b.user.username, b.session.title, b.session.date.strftime('%d.%m.%Y') if b.session.date else '', b.leave_time.strftime('%H:%M') if b.leave_time else '—', b.status_display] for b in qs]
        return generate_excel_response(headers, data, 'bookings_export')

class RoundViewSet(viewsets.ModelViewSet):
    queryset = Round.objects.all()
    serializer_class = RoundSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if session_id := self.request.query_params.get('session'): qs = qs.filter(session_id=session_id)
        if host_id := self.request.query_params.get('host'): qs = qs.filter(host_id=host_id)
        if mode_id := self.request.query_params.get('game_mode'): qs = qs.filter(game_mode_id=mode_id)
        return qs

    @action(detail=False, methods=['GET'], url_path='stats')
    def get_stats(self, request):
        stats = self.get_queryset().aggregate(count=Count('id'), mafia_wins=Count('id', filter=Q(winning_team='mafia')), town_wins=Count('id', filter=Q(winning_team='town')))
        return Response(RoundStatsSerializer(instance=stats).data)

    @action(detail=False, methods=['GET'], url_path='export')
    def export_excel(self, request):
        qs = self.get_queryset()
        headers = ['ID', 'Игра', 'Дата', 'Номер партии', 'Ведущий', 'Победитель']
        data = [[r.id, r.session.title, r.session.date.strftime('%d.%m.%Y') if r.session.date else '', r.number, r.host.username if r.host else '—', r.get_winning_team_display() or '—'] for r in qs]
        return generate_excel_response(headers, data, 'rounds_export')

class RoundPlayerViewSet(viewsets.ModelViewSet):
    queryset = RoundPlayer.objects.all()
    serializer_class = RoundPlayerSerializer

    @action(detail=False, methods=['GET'], url_path='stats')
    def get_stats(self, request):
        stats = self.get_queryset().aggregate(count=Count('id'), avg_points=Avg('points'), max_points=Max('points'), min_points=Min('points'))
        if stats['count'] == 0: return Response({"count": 0, "avg_points": 0, "max_points": 0, "min_points": 0})
        return Response(RoundPlayerStatsSerializer(instance=stats).data)

    @action(detail=False, methods=['GET'], url_path='export')
    def export_excel(self, request):
        qs = self.get_queryset()
        round_id = self.request.query_params.get('round')
        if round_id:
            qs = qs.filter(round_id=round_id)
        headers = ['ID', 'Игрок', 'Роль', 'Очки', 'Победа', 'Описание']
        data = [[rp.id, rp.user.username, rp.role, rp.points, 'Да' if rp.won else 'Нет', rp.description] for rp in qs]
        return generate_excel_response(headers, data, 'round_players_export')