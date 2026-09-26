from django.contrib import admin
from .models import Hotel, Booking, ContactMessage

#register the Hotel model
@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'city', 'price_per_night', 'address','number_of_rooms','default')  
    search_fields = ('name', 'city', 'address','price_per_night')  
    list_filter = ('city',)  
    ordering = ('id',)  
    
# Register the Booking model
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'email', 'phone_number', 'hotel', 'check_in_date', 'check_out_date', 'number_of_rooms', 'total_price', 'booking_date')
    search_fields = ('customer_name', 'email', 'hotel__name')
    list_filter = ('check_in_date', 'check_out_date', 'hotel')
# Register the ContactMessage model
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at')
    search_fields = ('name', 'email', 'subject')
    list_filter = ('created_at',)




    

