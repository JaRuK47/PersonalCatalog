from django.urls import path
from . import views

app_name = 'venue'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('schedule/', views.SessionListView.as_view(), name='schedule'),
    path('session/<int:pk>/', views.SessionDetailView.as_view(), name='session_detail'),
    path('my/bookings/', views.MyBookingsView.as_view(), name='my_bookings'),
]