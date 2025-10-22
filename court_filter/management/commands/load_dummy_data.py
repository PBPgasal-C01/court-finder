# court_filter/management/commands/load_dummy_data.py
# Script untuk load dummy data lapangan

from django.core.management.base import BaseCommand
from court_filter.models import Court, Province
from decimal import Decimal

class Command(BaseCommand):
    help = 'Load dummy court data for testing'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Loading dummy data...'))
        
        # Get or create provinces
        jakarta, _ = Province.objects.get_or_create(name='DKI Jakarta')
        jabar, _ = Province.objects.get_or_create(name='Jawa Barat')
        banten, _ = Province.objects.get_or_create(name='Banten')
        
        # Dummy courts data (sekitar Jakarta area)
        courts_data = [
            {
                'name': 'GOR Basket Senayan',
                'address': 'Jl. Asia Afrika, Gelora, Tanah Abang, Jakarta Pusat',
                'latitude': Decimal('-6.2188'),
                'longitude': Decimal('106.8019'),
                'court_type': 'basketball',
                'location_type': 'indoor',
                'price_per_hour': Decimal('150000'),
                'phone_number': '021-5701234',
                'description': 'Lapangan basket indoor dengan AC, lantai kayu berkualitas, tribun penonton. Cocok untuk kompetisi dan latihan rutin.',
                'provinces': [jakarta]
            },
            {
                'name': 'Lapangan Badminton Blok M Square',
                'address': 'Blok M Square Lt. 6, Jl. Melawai Raya, Kebayoran Baru, Jakarta Selatan',
                'latitude': Decimal('-6.2441'),
                'longitude': Decimal('106.7991'),
                'court_type': 'badminton',
                'location_type': 'indoor',
                'price_per_hour': Decimal('80000'),
                'phone_number': '021-7234567',
                'description': '6 lapangan badminton indoor ber-AC dengan standar nasional. Tersedia penyewaan raket dan shuttlecock.',
                'provinces': [jakarta]
            },
            {
                'name': 'Futsal Arena Kemang',
                'address': 'Jl. Kemang Raya No. 12, Bangka, Mampang Prapatan, Jakarta Selatan',
                'latitude': Decimal('-6.2615'),
                'longitude': Decimal('106.8166'),
                'court_type': 'futsal',
                'location_type': 'indoor',
                'price_per_hour': Decimal('200000'),
                'phone_number': '021-7190123',
                'description': 'Futsal arena premium dengan rumput sintetis kualitas internasional, lighting LED, dan kafe. Tersedia kamar ganti dan shower.',
                'provinces': [jakarta]
            },
            {
                'name': 'Tennis Court Ancol',
                'address': 'Jl. Lodan Timur No. 7, Ancol, Pademangan, Jakarta Utara',
                'latitude': Decimal('-6.1229'),
                'longitude': Decimal('106.8424'),
                'court_type': 'tennis',
                'location_type': 'outdoor',
                'price_per_hour': Decimal('120000'),
                'phone_number': '021-6402345',
                'description': 'Lapangan tenis outdoor dengan hard court surface, view pantai, dan suasana sejuk. 4 lapangan tersedia.',
                'provinces': [jakarta]
            },
            {
                'name': 'Lapangan Voli Pantai Marina',
                'address': 'Marina Beach, Jl. Boulevard Barat, Kelapa Gading, Jakarta Utara',
                'latitude': Decimal('-6.1577'),
                'longitude': Decimal('106.9098'),
                'court_type': 'volleyball',
                'location_type': 'outdoor',
                'price_per_hour': Decimal('100000'),
                'phone_number': '021-4528901',
                'description': 'Beach volleyball dengan pasir putih berkualitas, view laut, dan cafe pinggir pantai. Cocok untuk weekend games.',
                'provinces': [jakarta]
            },
            {
                'name': 'GOR Badminton Sudirman',
                'address': 'Jl. Jenderal Sudirman Kav. 52-53, Senayan, Jakarta Pusat',
                'latitude': Decimal('-6.2250'),
                'longitude': Decimal('106.8030'),
                'court_type': 'badminton',
                'location_type': 'indoor',
                'price_per_hour': Decimal('90000'),
                'phone_number': '021-5208765',
                'description': 'Gedung olahraga dengan 10 lapangan badminton, AC sentral, dan fasilitas lengkap termasuk mushola dan kantin.',
                'provinces': [jakarta]
            },
            {
                'name': 'Lapangan Basket Menteng',
                'address': 'Jl. Cikini Raya No. 89, Menteng, Jakarta Pusat',
                'latitude': Decimal('-6.1944'),
                'longitude': Decimal('106.8294'),
                'court_type': 'basketball',
                'location_type': 'outdoor',
                'price_per_hour': Decimal('75000'),
                'phone_number': '021-3145678',
                'description': 'Lapangan basket outdoor dengan pencahayaan baik untuk main malam. Lokasi strategis di tengah kota.',
                'provinces': [jakarta]
            },
            {
                'name': 'Futsal Center BSD',
                'address': 'Jl. Pahlawan Seribu, BSD City, Serpong, Tangerang Selatan',
                'latitude': Decimal('-6.3015'),
                'longitude': Decimal('106.6519'),
                'court_type': 'futsal',
                'location_type': 'indoor',
                'price_per_hour': Decimal('180000'),
                'phone_number': '021-7560123',
                'description': '3 lapangan futsal indoor dengan kualitas premium, sistem ventilasi baik, dan parkir luas.',
                'provinces': [banten]
            },
            {
                'name': 'Tennis Club Pondok Indah',
                'address': 'Jl. Metro Pondok Indah, Pondok Indah, Jakarta Selatan',
                'latitude': Decimal('-6.2663'),
                'longitude': Decimal('106.7839'),
                'court_type': 'tennis',
                'location_type': 'outdoor',
                'price_per_hour': Decimal('140000'),
                'phone_number': '021-7501234',
                'description': 'Tennis club dengan 6 lapangan outdoor dan 2 indoor. Tersedia pelatih profesional dan pro shop.',
                'provinces': [jakarta]
            },
            {
                'name': 'Lapangan Badminton Depok Town Square',
                'address': 'Depok Town Square, Jl. Margonda Raya, Depok, Jawa Barat',
                'latitude': Decimal('-6.3916'),
                'longitude': Decimal('106.8317'),
                'court_type': 'badminton',
                'location_type': 'indoor',
                'price_per_hour': Decimal('70000'),
                'phone_number': '021-7770456',
                'description': '8 lapangan badminton di dalam mall, AC dingin, parkir gratis. Dekat dengan food court dan bioskop.',
                'provinces': [jabar]
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for court_data in courts_data:
            provinces = court_data.pop('provinces')
            
            # Check if court already exists
            court, created = Court.objects.update_or_create(
                name=court_data['name'],
                defaults=court_data
            )
            
            # Add provinces
            court.provinces.set(provinces)
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created: {court.name}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'⟳ Updated: {court.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✅ Successfully loaded {created_count} new courts and updated {updated_count} existing courts!')
        )
        self.stdout.write(
            self.style.SUCCESS(f'📍 Total courts in database: {Court.objects.count()}')
        )