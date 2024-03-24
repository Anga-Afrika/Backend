from django.shortcuts import render, redirect
from .models import Warehouse, Compartment, Sensor
from .forms import SensorForm

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Warehouse, Compartment
from .serializers import CompartmentSerializer

@api_view(['POST'])
def create_warehouse(request):
    name = request.data.get('name')
    location = request.data.get('location')
    if name and location:
        warehouse = Warehouse.objects.create(name=name, location=location)
        return Response({'message': 'Warehouse created successfully'}, status=201)
    else:
        return Response({'error': 'Name and location are required'}, status=400)
    
def warehouse_list(request):
    warehouses = Warehouse.objects.all()
    return render(request, 'inventory/warehouse_list.html', {'warehouses': warehouses})

@api_view(['POST'])
def create_compartment(request):
    warehouse_name = request.data.get('warehouse_name')
    compartment_name = request.data.get('compartment_name')
    
    if warehouse_name and compartment_name:
        try:
            warehouse = Warehouse.objects.get(name=warehouse_name)
            compartment = Compartment.objects.create(name=compartment_name, warehouse=warehouse)
            return Response({'message': f'Compartment "{compartment_name}" created successfully in Warehouse "{warehouse_name}"'}, status=201)
        except Warehouse.DoesNotExist:
            return Response({'error': f'Warehouse "{warehouse_name}" not found'}, status=404)
    else:
        return Response({'error': 'Warehouse name and compartment name are required'}, status=400)

@api_view(['GET'])
def get_warehouses(request):
    warehouses = Warehouse.objects.all()
    data = [{'name': warehouse.name, 'location': warehouse.location} for warehouse in warehouses]
    return Response(data)

@api_view(['GET'])
def get_compartments(request):
    # Retrieve all compartments from the database
    compartments = Compartment.objects.all()

    # Convert compartments to JSON format
    data = [{'id': compartment.id, 'name': compartment.name} for compartment in compartments]

    # Return JSON response
    return Response(data)

@api_view(['POST'])
def add_sensor(request, compartment_id):
    try:
        compartment = Compartment.objects.get(id=compartment_id)
    except Compartment.DoesNotExist:
        return Response({'error': 'Compartment not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'POST':
        form = SensorForm(request.data)  # Assuming form data is sent in the request body
        if form.is_valid():
            sensor = form.save(commit=False)
            sensor.compartment = compartment
            sensor.save()
            return Response({'message': 'Sensor added successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error': 'Invalid request method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
@api_view(['GET'])
def compartment_detail(request, compartment_id):
    try:
        compartment = Compartment.objects.get(id=compartment_id)
    except Compartment.DoesNotExist:
        return Response({'error': 'Compartment not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = CompartmentSerializer(compartment)
    return Response(serializer.data)