from django.contrib import admin
from .models import User, WebhookEvent
admin.site.register(User)
admin.site.register(WebhookEvent)
# Register your models here.
