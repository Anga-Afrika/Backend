from django.db import models

class Warehouse(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)

    class Meta:
        app_label = 'inventory'  # Specify the app_label

    def __str__(self):
        return self.name

class Compartment(models.Model):
    name = models.CharField(max_length=100)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)

    class Meta:
        app_label = 'inventory'  # Specify the app_label

    def __str__(self):
        return self.name
    
class Sensor(models.Model):
    name = models.CharField(max_length=100)
    compartment = models.ForeignKey(Compartment, on_delete=models.CASCADE)

    def __str__(self):
        return self.name    
