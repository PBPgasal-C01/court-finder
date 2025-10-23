# court_filter/management/commands/populate_facilities.py
from django.core.management.base import BaseCommand
from manage_court.models import Facility 

class Command(BaseCommand):
    help = 'Populate basic facilities'

    def handle(self, *args, **options):
        facilities_data = [
            'Locker room',
            'Prayer room',
            'Showers',
            'Toilets / restrooms',
            'Changing room',
            'WiFi',
            'Canteen',
            'Drinking water station',
            'Parking area'
            'Air conditioning',
            'CCTV',
            'Sports equipment rental',
            
        ]
        
        for facility_name in facilities_data:
            facility, created = Facility.objects.get_or_create(name=facility_name)
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created facility: {facility_name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS('Successfully populated all facilities!')
        )