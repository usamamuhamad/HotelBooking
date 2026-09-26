import json
from django.core.management.base import BaseCommand
from booking_app.models import Hotel

class Command(BaseCommand):
    help = "Load hotels from a JSON file into the database"

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help='Path to the JSON file containing hotel data',
            required=True
        )

    def handle(self, *args, **kwargs):
        file_path = kwargs['file']

        try:
            # Open and load the JSON file
            with open(file_path, 'r') as file:
                hotels_data = json.load(file)

            # Iterate through the hotels and add them to the database
            for hotel_data in hotels_data:
                hotel, created = Hotel.objects.update_or_create(
                    name=hotel_data["name"],
                    defaults={
                        "city": hotel_data["city"],
                        "address": hotel_data["address"],
                        "price_per_night": hotel_data["price_per_night"],
                        "images": hotel_data["images"],
                        "default": hotel_data["default"],
                    },
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Added hotel: {hotel.name}"))
                else:
                    self.stdout.write(self.style.SUCCESS(f"Updated hotel: {hotel.name}"))

            self.stdout.write(self.style.SUCCESS("Hotels loaded successfully!"))

        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"File not found: {file_path}"))
        except json.JSONDecodeError:
            self.stderr.write(self.style.ERROR("Invalid JSON format"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"An error occurred: {e}"))