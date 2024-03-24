from django.urls import path
from .views import create_warehouse, create_compartment, get_warehouses, get_compartments, add_sensor, compartment_detail
from django.views.generic import TemplateView


urlpatterns = [
    path('register-warehouse/', TemplateView.as_view(template_name='inventory/register_warehouse.html'), name='register_warehouse'),
    path('add-compartment/', TemplateView.as_view(template_name='inventory/add_compartment.html'), name='add_compartment'),
    path('api/warehouse/create/', create_warehouse, name='create_warehouse'),
    path('api/compartment/create/', create_compartment, name='create_compartment'),
    path('api/warehouse/', get_warehouses, name='get_warehouses'),  # Define the route for retrieving warehouses
    # Add more URL routes for other API endpoints if needed
    path('api/compartment/', get_compartments, name='get_compartments'),
    path('api/compartment/<int:compartment_id>/add_sensor/', add_sensor, name='add_sensor'),
    path('compartment/<int:compartment_id>/', compartment_detail, name='compartment_detail'),
    # path('api/sensor/create/', add_sensor, name='add_sensor'),

]

