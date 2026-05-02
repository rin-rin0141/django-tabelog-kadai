from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import ListView
from restaurant.models import Restaurant, Category, Tag

class Top_displayView(ListView):
    model = Restaurant
    template_name = 'restaurant/restaurant_list.html'
    queryset = Restaurant.objects.filter(is_published=True)
    
    #htmlに渡す変数を追加するためのメソッド
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['tags'] = Tag.objects.all()
        return context
