from django.db import models
from accounts.models import User
import os

def upload_image_to(instance, filename):
    restaurant_id = str(instance.id)
    return os.path.join('images', restaurant_id, filename)

class Tag(models.Model):
    #slug = URLとかで使う識別用の文字列
    slug = models.CharField(max_length=32, primary_key=True)
    name = models.CharField(max_length=32)
    
    #管理画面でオブジェクトを表示する際の文字列を指定
    def __str__(self):
        return self.name
    
class Category(models.Model):
    slug = models.CharField(max_length=32, primary_key=True)
    name = models.CharField(max_length=32)
    
    def __str__(self):
        return self.name

class Restaurant(models.Model):
    name = models.CharField(max_length=100, blank=False)
    description = models.TextField(blank=False)
    price = models.PositiveIntegerField(default=0, blank=False)
    is_published = models.BooleanField(default=False)
    image = models.ImageField(default="", blank=True, upload_to=upload_image_to)
    #on_delete=models.SET_NULLは、Categoryが消された場合に、RestaurantのcategoryフィールドをNULLに設定する
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    
    
    def __str__(self):
        return self.name
    
class Review(models.Model):
    restaurant = models.ForeignKey(Restaurant, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=40, blank=False)
    content = models.TextField(blank=False)
    rating = models.PositiveIntegerField(default=0, blank=False)
    
    def star_display(self):
        return '⭐' * self.rating + '☆' * (5 - self.rating)
    
    def __str__(self):
        return self.title