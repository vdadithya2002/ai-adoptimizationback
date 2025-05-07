from rest_framework import serializers
from .models import User, AdCampaign, AdPerformance

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class AdCampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdCampaign
        fields = '__all__'

class AdPerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdPerformance
        fields = '__all__'
