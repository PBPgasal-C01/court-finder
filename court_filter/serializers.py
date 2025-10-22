from rest_framework import serializers
from .models import Court, Bookmark, Province

class ProvinceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = ['id', 'name']


class CourtSerializer(serializers.ModelSerializer):
    provinces = ProvinceSerializer(many=True, read_only=True)
    is_bookmarked = serializers.SerializerMethodField()
    distance = serializers.SerializerMethodField()

    class Meta:
        model = Court
        fields = [
            'id', 'name', 'address', 'latitude', 'longitude',
            'court_type', 'location_type', 'price_per_hour',
            'phone_number', 'description', 'provinces',
            'is_bookmarked', 'distance'
        ]

    def get_is_bookmarked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Bookmark.objects.filter(user=request.user, court=obj).exists()
        return False

    def get_distance(self, obj):
        distance = self.context.get('distance', {}).get(obj.id)
        return round(distance, 2) if distance else None
