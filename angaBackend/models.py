from django.db import models

# Create your models here.
class Threshold(models.Model):
    temperature_threshold = models.FloatField(default=0.0)
    humidity_threshold = models.FloatField(default=0.0)
LookupError