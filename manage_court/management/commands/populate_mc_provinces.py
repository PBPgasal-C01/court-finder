from django.core.management.base import BaseCommand
from manage_court.models import Province

class Command(BaseCommand):
    help = 'Populate Indonesia provinces'

    def handle(self, *args, **options):
        provinces_data = [
            'Aceh', 'Sumatera Utara', 'Sumatera Barat', 'Riau', 'Jambi',
            'Sumatera Selatan', 'Bengkulu', 'Lampung', 'Kepulauan Bangka Belitung',
            'Kepulauan Riau', 'DKI Jakarta', 'Jawa Barat', 'Jawa Tengah',
            'Daerah Istimewa Yogyakarta', 'Jawa Timur', 'Banten',
            'Bali', 'Nusa Tenggara Barat', 'Nusa Tenggara Timur',
            'Kalimantan Barat', 'Kalimantan Tengah', 'Kalimantan Selatan',
            'Kalimantan Timur', 'Kalimantan Utara', 'Sulawesi Utara',
            'Sulawesi Tengah', 'Sulawesi Selatan', 'Sulawesi Tenggara',
            'Gorontalo', 'Sulawesi Barat', 'Maluku', 'Maluku Utara',
            'Papua Barat', 'Papua', 'Papua Selatan', 'Papua Tengah',
            'Papua Pegunungan', 'Papua Barat Daya'
        ]
        
        for province_name in provinces_data:
            province, created = Province.objects.get_or_create(name=province_name)
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created province: {province_name}')
                )
            else:
                self.stdout.write(f'Province already exists: {province_name}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully populated all provinces!')
        )