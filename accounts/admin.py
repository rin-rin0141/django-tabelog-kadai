from django.contrib import admin
from .models import User, WebhookEvent

class UserAdmin(admin.ModelAdmin):
    search_fields = ["username"]
    
class WebhookEventAdmin(admin.ModelAdmin):
    search_fields = ["event_id", "event_type"]
    
admin.site.register(User, UserAdmin)
admin.site.register(WebhookEvent, WebhookEventAdmin)
    
