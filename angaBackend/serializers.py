from rest_framework import serializers
from .models import Threshold

class ThresholdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Threshold
        fields = ['temperature_threshold', 'humidity_threshold']
