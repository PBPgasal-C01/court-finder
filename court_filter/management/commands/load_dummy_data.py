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
        aceh, _ = Province.objects.get_or_create(name='Aceh')
        bali, _ = Province.objects.get_or_create(name='Bali')
        banten, _ = Province.objects.get_or_create(name='Banten')
        jakarta, _ = Province.objects.get_or_create(name='DKI Jakarta')
        jabar, _ = Province.objects.get_or_create(name='Jawa Barat')
        jateng, _ = Province.objects.get_or_create(name='Jawa Tengah')
        jatim, _ = Province.objects.get_or_create(name='Jawa Timur')
        diy, _ = Province.objects.get_or_create(name='D.I. Yogyakarta')
        kalbar, _ = Province.objects.get_or_create(name='Kalimantan Barat')
        sulsel, _ = Province.objects.get_or_create(name='Sulawesi Selatan')
        sumut, _ = Province.objects.get_or_create(name='Sumatera Utara')
        
        # Dummy courts data dari berbagai provinsi
        courts_data = [
            # ACEH
            {
                'name': 'LAPANGAN BOLA GAMPONG KUTA BAHAGIA',
                'address': 'Gampong Kuta Bahagia, Aceh Besar, Aceh',
                'latitude': Decimal('3.7392899'),
                'longitude': Decimal('96.8175558'),
                'court_type': 'soccer',
                'location_type': 'outdoor',
                'price_per_hour': Decimal('50000'),
                'phone_number': '081574247700',
                'description': 'Lapangan sepak bola outdoor dengan rumput alami, cocok untuk pertandingan kampung dan latihan rutin. Suasana sejuk pegunungan Aceh.',
                'provinces': [aceh]
            },
            {
                'name': 'LAPANGAN VOLI DESA MENASAH BAET',
                'address': 'Desa Menasah Baet, Aceh Utara, Aceh',
                'latitude': Decimal('5.5456093'),
                'longitude': Decimal('95.3640391'),
                'court_type': 'volleyball',
                'location_type': 'outdoor',
                'price_per_hour': Decimal('30000'),
                'phone_number': '084416771700',
                'description': 'Lapangan voli outdoor dengan lantai semen yang rata. Populer untuk pertandingan antar desa dan acara olahraga lokal.',
                'provinces': [aceh]
            },
            {
                'name': 'Stadion Mini Cilacap',
                'address': 'Cilacap, Aceh Besar, Aceh',
                'latitude': Decimal('5.2123295'),
                'longitude': Decimal('97.0566285'),
                'court_type': 'soccer',
                'location_type': 'outdoor',
                'price_per_hour': Decimal('100000'),
                'phone_number': '082985397400',
                'description': 'Stadion mini dengan fasilitas tribun penonton dan pencahayaan untuk pertandingan malam. Tersedia kamar ganti.',
                'provinces': [aceh]
            },
            
            # BALI
            {
                'name': 'Lapangan Tenis Undiksha',
                'address': 'Universitas Pendidikan Ganesha, Singaraja, Bali',
                'latitude': Decimal('-8.1163246'),
                'longitude': Decimal('115.091453'),
                'court_type': 'tennis',
                'location_type': 'outdoor',
                'price_per_hour': Decimal('80000'),
                'phone_number': '081653774400',
                'description': 'Lapangan tenis kampus dengan hard court berkualitas baik. Terbuka untuk umum di luar jam kuliah. View pegunungan.',
                'provinces': [bali]
            },
            {
                'name': 'Balai Bulutangkis Bina Pradnyan',
                'address': 'Jl. Raya Denpasar-Gilimanuk, Tabanan, Bali',
                'latitude': Decimal('-8.6597203'),
                'longitude': Decimal('115.2278909'),
                'court_type': 'badminton',
                'location_type': 'indoor',
                'price_per_hour': Decimal('70000'),
                'phone_number': '081403014000',
                'description': 'Gedung bulutangkis ber-AC dengan 4 lapangan standar nasional. Tersedia penyewaan raket dan shuttlecock.',
                'provinces': [bali]
            },
            {
                'name': 'Stadion Dipta',
                'address': 'Jl. Letda Tantular, Gianyar, Bali',
                'latitude': Decimal('-8.5196078'),
                'longitude': Decimal('115.3582415'),
                'court_type': 'soccer',
                'location_type': 'outdoor',
                'price_per_hour': Decimal('200000'),
                'phone_number': '081576389700',
                'description': 'Stadion sepak bola dengan kapasitas 5000 penonton, rumput alami terawat, dan fasilitas lengkap untuk pertandingan resmi.',
                'provinces': [bali]
            },
            {
                'name': 'Lapangan Basket SMA Negeri 2 Singaraja',
                'address': 'SMAN 2 Singaraja, Buleleng, Bali',
                'latitude': Decimal('-8.1291776'),
                'longitude': Decimal('115.0849345'),
                'court_type': 'basketball',
                'location_type': 'outdoor',
                'price_per_hour': Decimal('40000'),
                'phone_number': '087283385600',
                'description': 'Lapangan basket outdoor dengan ring standar dan lantai beton yang baik. Tersedia untuk umum di weekend.',
                'provinces': [bali]
            },
            
            # BANTEN
            {
                'name': 'BX Hoops Basketball Court',
                'address': 'BSD City, Tangerang Selatan, Banten',
                'latitude': Decimal('-6.2841985'),
                'longitude': Decimal('106.7285966'),
                'court_type': 'basketball',
                'location_type': 'indoor',
                'price_per_hour': Decimal('150000'),
                'phone_number': '083120728000',
                'description': 'Lapangan basket indoor premium dengan lantai parket, AC, dan lighting profesional. Cocok untuk latihan tim dan turnamen.',
                'provinces': [banten]
            },
            {
                'name': 'GOR Cihuni Jaya',
                'address': 'Jl. Cihuni, Tangerang, Banten',
                'latitude': Decimal('-6.2623635'),
                'longitude': Decimal('106.6289173'),
                'court_type': 'badminton',
                'location_type': 'indoor',
                'price_per_hour': Decimal('65000'),
                'phone_number': '083321984900',
                'description': 'Gedung olahraga dengan 6 lapangan badminton, AC sentral, dan kantin. Parkir luas tersedia.',
                'provinces': [banten]
            },
            {
                'name': 'Dewantara Sport Center',
                'address': 'Jl. Dewantara, Karawaci, Tangerang, Banten',
                'latitude': Decimal('-6.3444244'),
                'longitude': Decimal('106.6858614'),
                'court_type': 'soccer',
                'location_type': 'indoor',
                'price_per_hour': Decimal('180000'),
                'phone_number': '081523958500',
                'description': 'Futsal arena dengan rumput sintetis berkualitas tinggi, pencahayaan LED, dan fasilitas shower lengkap.',
                'provinces': [banten]
            },
            {
                'name': 'Padel Haus',
                'address': 'Alam Sutera, Tangerang Selatan, Banten',
                'latitude': Decimal('-6.2902408'),
                'longitude': Decimal('106.6371829'),
                'court_type': 'tennis',
                'location_type': 'outdoor',
                'price_per_hour': Decimal('200000'),
                'phone_number': '084407398100',
                'description': 'Lapangan padel pertama di Tangerang dengan standar internasional. Tersedia kelas untuk pemula dan pro shop.',
                'provinces': [banten]
            },
            
            # JAKARTA
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
                'court_type': 'soccer',
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
            
            # JAWA BARAT
            {
                'name': 'Badminton Tirta Sari',
                'address': 'Jl. Tirta Sari, Bekasi, Jawa Barat',
                'latitude': Decimal('-6.4030675'),
                'longitude': Decimal('106.8489675'),
                'court_type': 'badminton',
                'location_type': 'indoor',
                'price_per_hour': Decimal('60000'),
                'phone_number': '080711117100',
                'description': 'Lapangan badminton indoor dengan 5 court, AC, dan lantai karpet standar PB PBSI. Penyewaan peralatan tersedia.',
                'provinces': [jabar]
            },
            {
                'name': 'OSO Sport Center',
                'address': 'Jl. Raya Cikampek, Karawang, Jawa Barat',
                'latitude': Decimal('-6.286473'),
                'longitude': Decimal('107.0400677'),
                'court_type': 'soccer',
                'location_type': 'indoor',
                'price_per_hour': Decimal('170000'),
                'phone_number': '083564491200',
                'description': 'Futsal center modern dengan 2 lapangan indoor, rumput sintetis premium, dan cafe. Sistem booking online tersedia.',
                'provinces': [jabar]
            },
            {
                'name': 'Lapangan Tennis Bandung',
                'address': 'Jl. Dago Pakar, Bandung, Jawa Barat',
                'latitude': Decimal('-6.9289198'),
                'longitude': Decimal('107.7780972'),
                'court_type': 'tennis',
                'location_type': 'outdoor',
                'price_per_hour': Decimal('100000'),
                'phone_number': '085875576400',
                'description': 'Lapangan tenis outdoor dengan pemandangan kota Bandung. Hard court berkualitas, cocok untuk main pagi atau sore.',
                'provinces': [jabar]
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
            },
            
            # JAWA TENGAH
            {
                'name': 'Stadion Sriwedari',
                'address': 'Jl. Slamet Riyadi, Solo, Jawa Tengah',
                'latitude': Decimal('-7.568217'),
                'longitude': Decimal('110.8117486'),
                'court_type': 'soccer',
                'location_type': 'outdoor',
                'price_per_hour': Decimal('250000'),
                'phone_number': '087770776600',
                'description': 'Stadion bersejarah dengan kapasitas besar, rumput alami terawat, dan fasilitas lengkap. Venue untuk pertandingan liga.',
                'provinces': [jateng]
            },
            {
                'name': 'GOR Badminton Semarang',
                'address': 'Jl. Pandanaran, Semarang, Jawa Tengah',
                'latitude': Decimal('-7.0050651'),
                'longitude': Decimal('110.4383731'),
                'court_type': 'badminton',
                'location_type': 'indoor',
                'price_per_hour': Decimal('75000'),
                'phone_number': '082424508800',
                'description': '8 lapangan badminton dengan AC dingin, lantai vinyl standar internasional. Booking online tersedia.',
                'provinces': [jateng]
            },
            
            # JAWA TIMUR
            {
                'name': 'GOR Citra Surabaya',
                'address': 'Jl. Raya Darmo, Surabaya, Jawa Timur',
                'latitude': Decimal('-7.4156961'),
                'longitude': Decimal('111.4420502'),
                'court_type': 'volleyball',
                'location_type': 'indoor',
                'price_per_hour': Decimal('80000'),
                'phone_number': '088473813900',
                'description': 'Gedung olahraga untuk voli indoor dengan lantai kayu dan tribun penonton. Sering dipakai untuk kompetisi.',
                'provinces': [jatim]
            },
            {
                'name': 'Lapangan Basket SMAN 3 Jombang',
                'address': 'SMAN 3 Jombang, Jawa Timur',
                'latitude': Decimal('-7.5514224'),
                'longitude': Decimal('112.2295491'),
                'court_type': 'basketball',
                'location_type': 'outdoor',
                'price_per_hour': Decimal('35000'),
                'phone_number': '082245673400',
                'description': 'Lapangan basket outdoor dengan ring dan marking yang baik. Tersedia untuk umum di akhir pekan.',
                'provinces': [jatim]
            },
            {
                'name': 'PB Podo Seneng',
                'address': 'Jl. Banyuwangi, Jawa Timur',
                'latitude': Decimal('-8.3441529'),
                'longitude': Decimal('114.1203457'),
                'court_type': 'badminton',
                'location_type': 'indoor',
                'price_per_hour': Decimal('55000'),
                'phone_number': '082268025400',
                'description': 'Club badminton dengan 4 lapangan indoor, AC, dan pelatih tersedia. Cocok untuk latihan rutin.',
                'provinces': [jatim]
            },
            
            # YOGYAKARTA
            {
                'name': 'GOR Putra Sembada',
                'address': 'Jl. Nyi Pembayun, Sleman, DIY',
                'latitude': Decimal('-7.6576414'),
                'longitude': Decimal('110.328282'),
                'court_type': 'badminton',
                'location_type': 'indoor',
                'price_per_hour': Decimal('65000'),
                'phone_number': '083201384800',
                'description': 'GOR dengan 6 lapangan badminton standar nasional, AC, dan parkir luas. Dekat dengan UGM.',
                'provinces': [diy]
            },
            {
                'name': 'Tridadi Stadium',
                'address': 'Jl. Magelang Km 13, Sleman, DIY',
                'latitude': Decimal('-7.7195457'),
                'longitude': Decimal('110.3586469'),
                'court_type': 'soccer',
                'location_type': 'outdoor',
                'price_per_hour': Decimal('150000'),
                'phone_number': '084043420800',
                'description': 'Stadion dengan rumput alami dan atletik track. Fasilitas modern untuk pertandingan dan latihan.',
                'provinces': [diy]
            },
            
            # KALIMANTAN BARAT
            {
                'name': 'Lapangan Basket TCM',
                'address': 'Jl. Ahmad Yani, Pontianak, Kalbar',
                'latitude': Decimal('0.9024819'),
                'longitude': Decimal('108.9763459'),
                'court_type': 'basketball',
                'location_type': 'outdoor',
                'price_per_hour': Decimal('45000'),
                'phone_number': '089860685600',
                'description': 'Lapangan basket outdoor populer di Pontianak dengan ring standar dan lantai beton yang baik.',
                'provinces': [kalbar]
            },
            {
                'name': 'GOR Yafansa',
                'address': 'Jl. Sutoyo, Ketapang, Kalbar',
                'latitude': Decimal('-0.0522881'),
                'longitude': Decimal('109.3552127'),
                'court_type': 'badminton',
                'location_type': 'indoor',
                'price_per_hour': Decimal('50000'),
                'phone_number': '085789141400',
                'description': 'Gedung badminton dengan 5 lapangan, AC, dan fasilitas kantin. Cocok untuk turnamen lokal.',
                'provinces': [kalbar]
            },
            
            # SULAWESI SELATAN
            {
                'name': 'Dafest Sports Center',
                'address': 'Jl. Perintis Kemerdekaan, Makassar, Sulsel',
                'latitude': Decimal('-5.116196'),
                'longitude': Decimal('119.5058166'),
                'court_type': 'badminton',
                'location_type': 'indoor',
                'price_per_hour': Decimal('85000'),
                'phone_number': '087235718900',
                'description': 'Sports center modern dengan 10 lapangan badminton, AC dingin, dan pro shop lengkap. Parkir basement tersedia.',
                'provinces': [sulsel]
            },
            {
                'name': 'Lapangan Tennis Makassar',
                'address': 'Jl. Urip Sumoharjo, Makassar, Sulsel',
                'latitude': Decimal('-5.1418177'),
                'longitude': Decimal('119.464885'),
                'court_type': 'tennis',
                'location_type': 'outdoor',
                'price_per_hour': Decimal('90000'),
                'phone_number': '085514493800',
                'description': 'Lapangan tenis outdoor dengan 4 court hard surface dan pencahayaan untuk main malam.',
                'provinces': [sulsel]
            },
            
            # SUMATERA UTARA
            {
                'name': 'GOR Badminton Veteran',
                'address': 'Jl. Veteran, Medan, Sumut',
                'latitude': Decimal('3.5922308'),
                'longitude': Decimal('98.6851745'),
                'court_type': 'badminton',
                'location_type': 'indoor',
                'price_per_hour': Decimal('70000'),
                'phone_number': '082217764700',
                'description': 'GOR populer di Medan dengan 8 lapangan badminton, AC, dan fasilitas lengkap termasuk mushola.',
                'provinces': [sumut]
            },
            {
                'name': 'Futsal Arena Medan',
                'address': 'Jl. Gatot Subroto, Medan, Sumut',
                'latitude': Decimal('3.5642229'),
                'longitude': Decimal('98.6596804'),
                'court_type': 'soccer',
                'location_type': 'indoor',
                'price_per_hour': Decimal('160000'),
                'phone_number': '087701594000',
                'description': 'Futsal indoor dengan rumput sintetis berkualitas, AC, dan kafe. Sistem booking online tersedia.',
                'provinces': [sumut]
            },
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