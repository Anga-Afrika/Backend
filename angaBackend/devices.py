import json
import os
from django.conf import settings
from datetime import datetime
from uuid import uuid4

# Import client library classes
from influxdb_client import Authorization, Dialect, InfluxDBClient, Permission, PermissionResource, Point, WriteOptions
from influxdb_client.client.authorizations_api import AuthorizationsApi
from influxdb_client.client.bucket_api import BucketsApi
from influxdb_client.client.query_api import QueryApi
from influxdb_client.client.write_api import SYNCHRONOUS
from .sensor import Sensor
from influxdb_client.rest import ApiException


# Get configuration key-value pairs
def create_authorization(device_id) -> Authorization:

    influxdb_client = InfluxDBClient(
        url = settings.INFLUX_URL,
        token = settings.INFLUX_TOKEN+("=="),
        org = settings.INFLUX_ORG
    )

    authorization_api = AuthorizationsApi(influxdb_client)
    #Get the bucket_id
    buckets_api = BucketsApi(influxdb_client)
    buckets = buckets_api.find_bucket_by_name(settings.INFLUX_BUCKET)
    bucket_id = buckets.id
    org_id = buckets.org_id

    desc_prefix = f'AngaDevice: {device_id}'
    org_resource = PermissionResource(org_id=org_id, id=bucket_id, type="buckets")
    read = Permission(action="read", resource=org_resource)
    write = Permission(action="write", resource=org_resource)
    permissions = [read, write]
    authorization = Authorization(org_id=org_id, permissions=permissions, description=desc_prefix)
    request = authorization_api.create_authorization(authorization)
    return request

def create_device(device_id = None):
    influxdb_client = InfluxDBClient(
        url = settings.INFLUX_URL,
        token = os.getenv('INFLUX_TOKEN') + "==",
        org = settings.INFLUX_ORG
    )

    if device_id is None:
        device_id = str(uuid4())
    
    print(f"Device ID:::::::::::::::::::::::::{device_id}")
    write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)
    point = Point('deviceauth') \
        .tag('deviceId', device_id) \
        .field('key', f'fake_auth_id_{device_id}') \
        .field('token', f'fake_auth_token_{device_id}')
    
    print(f"Point:::::::::::::::::::::::::{point.to_line_protocol()}")
    
    client_response = write_api.write(bucket=settings.INFLUX_BUCKET_AUTH, record=point)

    print(f"Client Response:::::::::::::::::::::::::{client_response}")
    #write() returns None on success
    if client_response is None:
        return device_id
    # Return None on failure
    return None

def get_device(device_id = None):
    influxdb_client = InfluxDBClient(
        url = settings.INFLUX_URL,
        token = os.getenv('INFLUX_TOKEN') + "==",
        org = settings.INFLUX_ORG
    )

    print(f"Device ID:::::::::::::::::::::::::{device_id}")
    

    query_api = QueryApi(influxdb_client)
    device_filter = ''
    if device_id:
        device_id = str(device_id)
        device_filter = f'r.deviceId == "{device_id}" and r._field != "token"'
        print(f"i am here:::::::::::::::::::::::::{device_filter}")
    else:
        device_filter = 'r._field != "token"'
        print(f"i am elsing:::::::::::::::::::::::::{device_filter}")
    
    flux_query =f'from(bucket: "{settings.INFLUX_BUCKET_AUTH}") ' \
                f'|> range(start: 0) ' \
                f'|> filter(fn: (r) => r._measurement == "deviceauth" and {device_filter})' \
                f'|> last()'
    # print(f"Flux Query:::::::::::::::::::::::::{flux_query}")
    response = query_api.query(flux_query)
    # print(f"Response:::::::::::::::::::::::::{response}")
    result = []
    for table in response:
        for record in table.records:
            try:
                'updatedAt' in record
            except KeyError:
                record['updatedAt'] = record.get_time()
                record[record.get_field()] = record.get_value()
            result.append(record.values)
    return result

def get_measurements(query):
    # print(f"Query:::::::::::::::::::::::::{query}")
    influxdb_client = InfluxDBClient(
        url = settings.INFLUX_URL,
        token = settings.INFLUX_TOKEN+("=="),
        org = settings.INFLUX_ORG
    )
    print(f"token::::{influxdb_client.token}")
    query_api = QueryApi(influxdb_client)
    
    try:
        # Perform the Flux query to get the raw data
        result = query_api.query(query)
        data = [entry for table in result for entry in table.records]
        moving_average_window_size = 3

        # Calculate the moving average
        moving_average_data = calculate_moving_average(data, moving_average_window_size)

        # Convert the result to the desired format
        formatted_result = {timestamp: value for timestamp, value in moving_average_data.items()}


        # Convert the formatted result to JSON
        # json_result = json.dumps(formatted_result, indent=2)

        return formatted_result

    except ApiException as e:
        # Handle exception if the query fails
        return {"error": str(e)}

def calculate_moving_average(data, window_size):
    result = {}

    for i in range(len(data)):
        timestamp = data[i]['_time'].timestamp()  # Ensure timestamp is a string
        values = [entry['_value'] for entry in data[max(0, i - window_size + 1):i + 1]]
        valid_values = [value for value in values if value is not None]

        if valid_values:
            average = sum(valid_values) / len(valid_values)
            result[timestamp] = average

    return result

