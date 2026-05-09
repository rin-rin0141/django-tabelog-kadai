from django.contrib import admin
from .models import Reservation

class ReservationAdmin(admin.ModelAdmin):
    list_display = ('user', 'restaurant', 'reservation_date', 'reservation_time', 'number_of_people', 'status')
    list_filter = ('status', 'reservation_date')
    search_fields = ('user__username', 'restaurant__name')

admin.site.register(Reservation, ReservationAdmin)
