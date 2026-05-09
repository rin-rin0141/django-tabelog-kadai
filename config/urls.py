from django.contrib import admin
from django.urls import path, include
from base.views import Top_displayView
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    # Adminサイト
    path('admin/', admin.site.urls),
    
    # トップページ
    path('', Top_displayView.as_view(), name='top_display'),
    
    # レストランアプリのURL
    path('restaurant/', include('restaurant.urls')),
    
    # アカウントアプリのURL
    path('accounts/', include('accounts.urls')),
    
    # 予約アプリのURL
    path('reservations/', include('reservations.urls')),
]

# 開発環境時のみ/media/... にアクセスが来たら、MEDIA_ROOT の中を見せる
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)