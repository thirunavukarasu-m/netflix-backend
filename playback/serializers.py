from rest_framework import serializers
from .models import Device, WatchSession, SubscriptionPlan, UserSubscriptionPlan, Movie

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = "__all__"
    
class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = "__all__"

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