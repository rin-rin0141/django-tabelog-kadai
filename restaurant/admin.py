from django.contrib import admin
from .models import Restaurant, Category, Tag, Review
admin.site.register(Restaurant)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Review)

# Register your models here.
