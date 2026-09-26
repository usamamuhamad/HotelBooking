from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import ContactMessage, Hotel, Feedback, Booking
from .forms import BookingForm  
from django.views.decorators.csrf import csrf_exempt
import json
import re
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.db.models import Q

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password.")  # Error message
    return render(request, "login.html")

def signup_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")  # Error message
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            return redirect("home")
    return render(request, "signup.html")

def logout_view(request):
    logout(request)
    return redirect("home")

def hotels_by_city(request, city):
    # Replace this with your actual hotel filtering logic
    hotels = [
        {"name": "Hotel Crown Lahore", "city": "Lahore", "address": "276, Block R2, Lahore"},
        {"name": "Grand Pakeeza Hotel", "city": "Lahore", "address": "R2 Block Road 57, Lahore"},
        {"name": "Best Western Premier", "city": "Islamabad", "address": "110 MM Alam Road, Islamabad"},
    ]
    filtered_hotels = [hotel for hotel in hotels if hotel["city"].lower() == city.lower()]
    return render(request, 'hotel.html', {'city': city, 'hotels': filtered_hotels})



def success(request):
    return render(request, "success.html")


# Create your views here.




def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        # Save the message to the database
        ContactMessage.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        messages.success(request, "Your message has been sent successfully!")
        return redirect("contact")  # Redirect to the contact page after submission

    return render(request, 'contact.html')



def about(request):
    return render(request, 'about.html')

def home(request):
    query = request.GET.get('query', '').strip().lower()
    city = request.GET.get('city', '').strip().lower()

    if query:
        hotels = Hotel.objects.filter(name__icontains=query, default=False)
    elif city:
        hotels = Hotel.objects.filter(city__iexact=city, default=False)
    else:
        hotels = Hotel.objects.filter(default=True)  # Only fetch default hotels
    
    return render(request, 'base.html', {'hotels': hotels})
 # Ensure 'home.html' extends 'base.html'

def support(request):
    return render(request, 'support.html')

def hotels(request):
    return render(request, 'hotel.html')

# changes made on 28/03/2025



@login_required
def submit_feedback(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)

    if request.method == "POST":
        rating = int(request.POST.get("rating"))
        comment = request.POST.get("comment")

        # Ensure the user has stayed at the hotel (logic depends on your booking system)
        # For example, check if the user has a completed booking for this hotel
        # if not user_has_stayed_at_hotel(request.user, hotel):
        #     return JsonResponse({"error": "You can only leave feedback for hotels you have stayed in."}, status=403)

        Feedback.objects.create(
            hotel=hotel,
            user=request.user,
            rating=rating,
            comment=comment,
        )
        return JsonResponse({"success": "Feedback submitted successfully."})

    return JsonResponse({"error": "Invalid request method."}, status=400)

def get_hotels(request):
    query = request.GET.get('query', '').strip().lower()
    city = request.GET.get('city', '').strip().lower()

    try:
        # Filter hotels based on query and city
        if city == "all":  # Show all hotels
            hotels = Hotel.objects.all()
        elif city:  # Filter by city
            hotels = Hotel.objects.filter(city__icontains=city)
        elif query:  # Search by hotel name
            hotels = Hotel.objects.filter(name__icontains=query)
        else:  # Default behavior: show only default hotels
            hotels = Hotel.objects.filter(default=True)

        hotels_data = []
        for hotel in hotels:
            # Use the `images` field directly (it's a JSONField storing a list of image paths)
            images = hotel.images if hotel.images else ["/static/images/placeholder.jpg"]  # Fallback placeholder image

            # Add hotel data
            hotels_data.append({
                "id": hotel.id,
                "name": hotel.name,
                "city": hotel.city,
                "price_per_night": hotel.price_per_night,
                "address": hotel.address,
                "images": images,
                "amenities": hotel.amenities,  # Directly use the `amenities` JSONField
            })

        return JsonResponse({"hotels": hotels_data})
    except Exception as e:
        # Log the error and return a 500 response
        print(f"Error in get_hotels view: {e}")
        return JsonResponse({"error": "An error occurred while fetching hotels."}, status=500)
    




@csrf_exempt
def save_booking(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            print(f"Received data: {data}")  # Debugging

            # Extract and validate required fields
            customer_name = data.get("customer_name")
            email = data.get("email")
            phone_number = data.get("phone_number")
            check_in_date = data.get("check_in_date")
            check_out_date = data.get("check_out_date")
            number_of_rooms = int(data.get("number_of_rooms"))
            total_price = data.get("total_price")
            hotel_id = data.get("hotel_id")
            card_number = data.get("card_number")

            if not all([customer_name, email, phone_number, check_in_date, check_out_date, number_of_rooms, total_price, hotel_id, card_number]):
                return JsonResponse({"error": "Missing required fields."}, status=400)

            # Validate card number
            if not validate_card_number(card_number):
                return JsonResponse({"error": "Invalid card number. Only Visa and MasterCard are accepted."}, status=400)

            # Retrieve the related Hotel instance
            try:
                hotel = Hotel.objects.get(id=hotel_id)
            except Hotel.DoesNotExist:
                return JsonResponse({"error": "Hotel not found."}, status=404)
            
             # Check room availability
            is_available, available_rooms = check_room_availability(hotel, check_in_date, check_out_date, number_of_rooms)
            if not is_available:
                return JsonResponse({"error": f"Only {available_rooms} rooms are available for the selected dates."}, status=400)

            # Create and save the Booking object
            booking = Booking.objects.create(
                customer_name=customer_name,
                email=email,
                phone_number=phone_number,
                check_in_date=check_in_date,
                check_out_date=check_out_date,
                number_of_rooms=number_of_rooms,
                total_price=total_price,
                hotel=hotel,
            )
            print(f"Booking saved: {booking}")  # Debugging
            

            # Send confirmation email
            subject = "Booking Confirmation - HotelBookingPK"
            html_message = render_to_string('emails/booking_confirmation.html', {
                'customer_name': customer_name,
                'hotel_name': hotel.name,
                'check_in_date': check_in_date,
                'check_out_date': check_out_date,
                'number_of_rooms': number_of_rooms,
                'total_price': total_price,
            })
            plain_message = strip_tags(html_message)
            from_email = 'usa032039@gmail.com'
            to_email = email

            email = EmailMessage(subject, plain_message, from_email, [to_email])
            email.content_subtype = "html"  # Send as HTML
            email.send()

            return JsonResponse({"success": "Booking confirmed! A confirmation email has been sent."})
        except Exception as e:
            print(f"Error in save_booking: {e}")  # Debugging
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid request method."}, status=400)
            


def validate_card_number(card_number):
    """
    Validate the card number for Visa and MasterCard.
    Visa: Starts with 4, 16 digits.
    MasterCard: Starts with 51-55 or 2221-2720, 16 digits.
    """
    visa_pattern = r"^4\d{15}$"
    mastercard_pattern = r"^(5[1-5]\d{14}|2(2[2-9]\d{12}|[3-6]\d{13}|7[01]\d{12}|720\d{12}))$"

    if re.match(visa_pattern, card_number) or re.match(mastercard_pattern, card_number):
        return True
    return False



def check_room_availability(hotel, check_in_date, check_out_date, requested_rooms):
    # Get all bookings for the hotel that overlap with the selected dates
    overlapping_bookings = Booking.objects.filter(
        hotel=hotel,
        check_in_date__lt=check_out_date,
        check_out_date__gt=check_in_date
    )

    # Calculate the total rooms already booked for the overlapping dates
    rooms_booked = sum(booking.number_of_rooms for booking in overlapping_bookings)

    # Check if the requested rooms exceed the available rooms
    available_rooms = hotel.number_of_rooms - rooms_booked
    return available_rooms >= requested_rooms, available_rooms