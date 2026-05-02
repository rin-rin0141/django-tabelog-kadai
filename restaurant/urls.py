from django.urls import path
from .views import RestaurantDetailView, search_result, category_result, tag_result, reviewkeep

app_name = 'restaurant'

urlpatterns = [
    # Items
    path('items/<int:pk>/', RestaurantDetailView.as_view(), name='restaurant_detail'),
    path('search/', search_result, name='search'),
    path('tag/<str:slug>/', tag_result, name='tag_search'),
    path('category/<str:slug>/', category_result, name='category_search'),
    path('review/<int:pk>/', reviewkeep, name='reviewkeep'),
]
