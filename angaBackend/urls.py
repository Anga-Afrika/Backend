from django.urls import path

from . import views

urlpatterns = [
    # path('', views.index, name='index')
    path('api/devices/', views.get_devices, name='get_device'),
    path('api/create/', views.create_devices, name='create_device'),
    path('api/getdata/', views.get_data, name='get_data'),
    path('api/temp-average/', views.get_weekly_temp_average, name='get_temp_average'),
    path('api/humidity-average/', views.get_weekly_humidity_average, name='get_humidity_average'),
    path('api/threshold/', views.threshold_api, name='threshold_api'),
    path('api/humidity_extremes/', views.get_weekly_humidity_extremes, name='humidity_extremes'),
    path('api/temperature_extremes/', views.get_weekly_temp_extremes, name='temperature_extremes'),
]