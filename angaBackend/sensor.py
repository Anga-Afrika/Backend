# sensors/utils.py
import json
import random
import urllib3
from django.core.exceptions import ImproperlyConfigured

http = urllib3.PoolManager()

def fetch_json(url):
    """Fetch JSON from url."""
    response = http.request('GET', url)
    if not 200 <= response.status <= 299:
        raise ImproperlyConfigured(f'[HTTP - {response.status}]: {response.reason}')
    return json.loads(response.data.decode('utf-8'))

class Sensor:
    def __init__(self):
        self.id = ''
        self.temperature = None
        self.pressure = None
        self.humidity = None

    def generate_measurement(self):
        """Generate random measurement for simulation purposes."""
        return round(random.uniform(0, 100))

    def get_geo_location(self):
        """
        Get GEO location from 'https://freegeoip.app/json/'.
        :return: Returns a dictionary with `latitude` and `longitude` key.
        """
        try:
            geo_data = fetch_json('https://freegeoip.app/json/')
            return {
                'latitude': geo_data.get('latitude'),
                'longitude': geo_data.get('longitude'),
            }
        except Exception as e:
            return {
                'latitude':  self.generate_measurement(),
                'longitude':  self.generate_measurement(),
            }
