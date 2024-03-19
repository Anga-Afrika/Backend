import json
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework import status 
from rest_framework.response import Response
from datetime import datetime, timedelta

from angaBackend.models import Threshold
from angaBackend.serializers import ThresholdSerializer
from .devices import get_device, create_device, get_measurements
from django.conf import settings


# Create your views here.
@api_view(['GET', 'POST', 'OPTIONS'])
def get_devices(request):
    device_id = request.query_params.get('device_id')
    if request.method == 'OPTIONS': # CORS preflight request
        return Response(status = 204)
    device_data = get_device(device_id)

    return Response(device_data)

@api_view(['POST'])
def create_devices(request, device_id = None):
    #call the create_device function
    device_data = create_device(device_id)
    return Response(device_data)
    
# @api_view(['POST'])
# def write_measurement(request):
#     #call the write_measurements function
#     device_id = request.data.get('device_id')
#     print(f"Device ID:::::::::::::::::::::::::{request.data}")
#     device_data = write_measurements(device_id)
#     return JsonResponse(device_data)    

@api_view(['POST'])
def get_data(request):
    #call the get_measurements function
    query = request.data.get('query')
    device_data = get_measurements(query)
    return JsonResponse(device_data, safe=False)

@api_view(['GET'])
def get_weekly_temp_average(request):
    # Calculate the start and stop times for the previous day
    today = datetime.today()
    start_time = (today - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    end_time = today.replace(hour=0, minute=0, second=0, microsecond=0)

    # Construct the Flux query for the previous day's temperature data
    flux_query = f"from(bucket: \"SensorData\")\n  |> range(start: -7d, stop: -1d)\n  |> filter(fn: (r) => r[\"_measurement\"] == \"mqtt_consumer\")\n  |> filter(fn: (r) => r[\"_field\"] == \"temperature\")\n  |> filter(fn: (r) => r[\"host\"] == \"local.mqtt.telegraf\")\n  |> filter(fn: (r) => r[\"topic\"] == \"iot/device/telemetry\")\n  |> aggregateWindow(every:  10m, fn: mean, createEmpty: false)\n  |> yield(name: \"mean\")"

    # Fetch the data using the existing get_measurements function
    result = get_measurements(flux_query)

    # Calculate the mean of the temperature values
    temperatures = [float(value) for value in result.values()]
    if temperatures:
        mean_temperature = sum(temperatures) / len(temperatures)
    else:
        mean_temperature = None

    # Return the mean as JSON
    return JsonResponse({"mean_temperature": mean_temperature})

@api_view(['GET'])
def get_weekly_humidity_average(request):
    # Calculate the start and stop times for the previous day
    today = datetime.today()
    start_time = (today - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    end_time = today.replace(hour=0, minute=0, second=0, microsecond=0)

    # Construct the Flux query for the previous day's temperature data
    flux_query = f"from(bucket: \"SensorData\")\n  |> range(start:-7d, stop:-1d)\n  |> filter(fn: (r) => r[\"_measurement\"] == \"mqtt_consumer\")\n  |> filter(fn: (r) => r[\"_field\"] == \"humidity\")\n  |> filter(fn: (r) => r[\"host\"] == \"local.mqtt.telegraf\")\n  |> filter(fn: (r) => r[\"topic\"] == \"iot/device/telemetry\")\n  |> aggregateWindow(every:  1d, fn: mean, createEmpty: false)\n  |> yield(name: \"mean\")"

    # Fetch the data using the existing get_measurements function
    result = get_measurements(flux_query)

    # Calculate the mean of the temperature values
    humidity = [float(value) for value in result.values()]
    if humidity:
        mean_humidity = sum(humidity) / len(humidity)
    else:
        mean_humidity = None

    # Return the mean as JSON
    return JsonResponse({"mean_humidity": mean_humidity})

@api_view(['PATCH', 'POST','GET'])
def threshold_api(request):
    try:
        threshold = Threshold.objects.first()
    except Threshold.DoesNotExist:
        return Response({"error": "Threshold not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'POST':
        serializer = ThresholdSerializer(threshold, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'PATCH':
        serializer = ThresholdSerializer(threshold, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'GET':
        serializer = ThresholdSerializer(threshold)
        return Response(serializer.data, status=status.HTTP_200_OK)    

@api_view(['GET'])
def get_weekly_humidity_extremes(request):
    flux_query = f"from(bucket: \"SensorData\")\n  |> range(start:-60d)\n  |> filter(fn: (r) => r[\"_measurement\"] == \"mqtt_consumer\")\n  |> filter(fn: (r) => r[\"_field\"] == \"humidity\")\n  |> filter(fn: (r) => r[\"host\"] == \"local.mqtt.telegraf\")\n  |> filter(fn: (r) => r[\"topic\"] == \"iot/device/telemetry\")\n  |> aggregateWindow(every:  10m, fn: mean, createEmpty: false)\n  |> yield(name: \"mean\")"

    extremes_data = get_measurements(flux_query)
    print(f"Extremes Data:::::::::::::::::::::::::{extremes_data}")
    humidity = [float(value) for value in extremes_data.values()]
    if humidity:
        min_humidity = min(humidity)
        max_humidity = max(humidity)
    else:
        min_humidity = None
        max_humidity = None
    
    return JsonResponse({"min_humidity": min_humidity, "max_humidity": max_humidity})

@api_view(['GET'])
def get_weekly_temp_extremes(request):
    flux_query = f"from(bucket: \"SensorData\")\n  |> range(start: -60d, stop: -1d)\n  |> filter(fn: (r) => r[\"_measurement\"] == \"mqtt_consumer\")\n  |> filter(fn: (r) => r[\"_field\"] == \"temperature\")\n  |> filter(fn: (r) => r[\"host\"] == \"local.mqtt.telegraf\")\n  |> filter(fn: (r) => r[\"topic\"] == \"iot/device/telemetry\")\n  |> aggregateWindow(every:  10m, fn: mean, createEmpty: false)\n  |> yield(name: \"mean\")"

    extremes_data = get_measurements(flux_query)
    print(f"Extremes Data:::::::::::::::::::::::::{extremes_data}")
    temp = [float(value) for value in extremes_data.values()]
    if temp:
        min_temp = min(temp)
        max_temp = max(temp)
    else:
        min_temp = None
        max_temp = None
    
    return JsonResponse({"min_temp": min_temp, "max_temp": max_temp})
