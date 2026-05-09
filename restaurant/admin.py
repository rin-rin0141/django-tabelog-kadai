from django.contrib import admin
from .models import Restaurant, Category, Tag, Review

class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_published')
    list_filter = ('category', 'is_published')
    search_fields = ('name', 'description')

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('title', 'restaurant', 'user', 'rating')
    list_filter = ('rating',)
    search_fields = ('title', 'content')
    
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    
class TagAdmin(admin.ModelAdmin):
    search_fields = ('name',)

admin.site.register(Restaurant, RestaurantAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Review, ReviewAdmin)
