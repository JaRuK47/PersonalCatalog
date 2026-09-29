from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from venue.api import (
    VenueViewSet, SessionViewSet, BookingViewSet,
    RoundViewSet, RoundPlayerViewSet,
)

router = DefaultRouter()
router.register('venues', VenueViewSet, basename='venue')
router.register('sessions', SessionViewSet, basename='session')
router.register('bookings', BookingViewSet, basename='booking')
router.register('rounds', RoundViewSet, basename='round')
router.register('round-players', RoundPlayerViewSet, basename='round-player')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('', include('venue.urls')),
]