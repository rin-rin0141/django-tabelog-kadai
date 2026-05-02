from django import forms
from .models import Reservation

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ('reservation_date', 'reservation_time', 'number_of_people')

    reservation_date = forms.DateField(required=True)
    reservation_time = forms.TimeField(required=True)
    number_of_people = forms.IntegerField(min_value=1, required=True)