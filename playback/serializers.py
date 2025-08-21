from rest_framework import serializers
from .models import Device, WatchSession, SubscriptionPlan, UserSubscriptionPlan, Movie, Genre

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["id", "name", "slug"]

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = "__all__"
    
class MovieSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)
    genre_ids = serializers.PrimaryKeyRelatedField(
        many=True, write_only=True, queryset=Genre.objects.all(), source="genres"
    )

    class Meta:
        model = Movie
        fields = [
            "id", "movie_id", "title", "duration", "cdn_path", "is_active",
            "description", "release_year", "maturity_rating", "language",
            "genres", "genre_ids", "cast", "directors", "tags",
            "created_at", "updated_at",
        ]

class UserSubscriptionPlanSerializer(serializers.ModelSerializer):
    plan = SubscriptionPlanSerializer()
    class Meta:
        model = UserSubscriptionPlan
        fields = "__all__"

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ('device_id','name','device_type')

class WatchSessionSerializer(serializers.ModelSerializer):
    movie = MovieSerializer(read_only=True)
    device = DeviceSerializer(read_only=True)
    class Meta:
        model = WatchSession
        fields = ('id','movie','device','started_at','last_heartbeat','status')
