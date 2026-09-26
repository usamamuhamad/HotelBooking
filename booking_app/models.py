from django.db import models
from django.contrib.auth.models import User  



class Hotel(models.Model):
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    address = models.TextField()
    images = models.JSONField(default=list, blank=True) 
    default = models.BooleanField(default=True)
    amenities = models.JSONField(default=list, blank=True)  
    number_of_rooms = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Hotels"




class Booking(models.Model):
    customer_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    number_of_rooms = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    booking_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer_name} - {self.hotel.name}"

class ContactMessage(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"

class Feedback(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="feedbacks")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=[(i, f"{i} Star") for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.hotel.name} ({self.rating} Stars)"
    
