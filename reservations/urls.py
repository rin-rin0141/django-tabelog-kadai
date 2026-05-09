from django.urls import path
from . import views

app_name = 'reservations'

urlpatterns = [
     # Account
     path('reservation/<int:pk>/', views.CustomReservationView.as_view(), name='reservation'),
     path('receiving-webhook/', views.ReceivingWebhookView.as_view(), name='receiving_webhook'),
     path('reservation_success/', views.ReservationSuccessView.as_view(), name='reservation_success'),
     path('reservation_failed/', views.ReservationFailedView.as_view(), name='reservation_failed'),
     #path('history/', views.HistoryView.as_view(), name='history'),
]

