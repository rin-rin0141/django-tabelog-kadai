from django.db import models
from restaurant.models import Restaurant
from accounts.models import User

class Reservation(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reservation_date = models.DateField()
    reservation_time = models.TimeField()
    number_of_people = models.IntegerField()
    status = models.CharField(max_length=20, default='pending')
    
    def __str__(self):
        return self.user.username
