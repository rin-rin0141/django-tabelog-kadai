from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
     # Account
     path('signup/', views.SignUpView.as_view(), name='signup'),
     path('login/', views.CustomLoginView.as_view(), name='login'),
     path('logout/', views.CustomLogoutView.as_view(), name='logout'),
     path('mypage/', views.MypageView.as_view(), name='mypage'),
     path('password_change/', views.CustomPasswordChangeView.as_view(), name='password_change'),
     path('password_change_done/', views.PasswordChangeDoneView.as_view(), name='password_change_done'),
     path('subscribe/', views.CustomSubscribeView.as_view(), name='subscribe'),
     path('cancel_subscribe/', views.CancelSubscribeView.as_view(), name='cancel_subscribe'),
     path('resume_subscribe/', views.ResumeSubscribeView.as_view(), name='resume_subscribe'),
     path('subscribe_success/', views.SuccessSubscribeView.as_view(), name='subscribe_success'),
     path('subscribe_failed/', views.FailedSubscribeView.as_view(), name='subscribe_failed'),
     path('webhook/', views.ReceivingWebhookView.as_view(), name='webhook'),
     path('history/', views.HistoryView.as_view(), name='history'),
     path('cancel_reservation/<int:pk>/', views.CancelReservationView.as_view(), name='cancel_reservation'),
]