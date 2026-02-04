from django.db import models
import datetime
from django.contrib.auth import get_user_model

User = get_user_model()
from taberogumodoki.models.item_models import Item


def custom_timestamp_id():
    dt = datetime.datetime.now()
    return dt.strftime("%Y%m%d%H%M%S%f")


class Order(models.Model):
    id = models.CharField(
        default=custom_timestamp_id, editable=False, primary_key=True, max_length=50
    )
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    uid = models.CharField(editable=False, max_length=50)
    is_confirmed = models.BooleanField(default=False)
    amount = models.PositiveIntegerField(default=0)
    tax_included = models.PositiveIntegerField(default=0)
    items = models.JSONField()
    shipping = models.JSONField()
    shipped_at = models.DateTimeField(blank=True, null=True)
    canceled_at = models.DateTimeField(blank=True, null=True)
    memo = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reserve_date = models.DateField()
    reserve_time = models.CharField(max_length=5)
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_session_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.id


class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.item}"
