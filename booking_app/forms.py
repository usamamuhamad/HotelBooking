from django import forms
from .models import Booking

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [
            'customer_name',
            'email',
            'phone_number',
            'check_in_date',
            'check_out_date',
            'number_of_rooms',
            'total_price',
            'hotel',
        ]
 
 