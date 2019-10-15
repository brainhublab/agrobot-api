import requests
import os
import json


GLOBAL_SERVER_RAW_DATA_ROUTE = os.environ.get("GLOBAL_SERVER_RAW_DATA_ROUTE")
GLOBAL_SERVER_SENSORS_ROUTE = os.environ.get("GLOBAL_SERVER_SENSORS_ROUTE")

token = "fe742bcb7bfa0c3ff680be5f84118321c2d2088b"


def create_request_header(token):
    return {'Authorization': 'Bearer {}'.format(token)}


def get_sensor_raw_data(token,
                        obj_id=None,
                        sensor_id=None,
                        sensor__sensor_type_id=None,
                        sensor__controller_id=None,
                        sensor__controller__sector_id=None,
                        sensor__controller__sector__workspace_id=None,
                        from_date=None,
                        to_date=None):

    headers = create_request_header(token)
    url = GLOBAL_SERVER_RAW_DATA_ROUTE
    if obj_id:
        if (isinstance(obj_id, int)):
            url = url + '{}/'.format(obj_id)
    else:
        url = url + "?"

        if sensor_id:
            if (isinstance(sensor_id, int)):
                url = url + 'sensor_id={}&'.format(sensor_id)
        if sensor__sensor_type_id:
            if (isinstance(sensor__sensor_type_id, int)):
                url = url + 'sensor__sensor_type_id={}&'.format(sensor__sensor_type_id)
        if sensor__controller_id:
            if (isinstance(sensor__controller_id, int)):
                url = url + 'sensor__controller_id={}&'.format(sensor__controller_id)
        if sensor__controller__sector_id:
            if (isinstance(sensor__controller__sector_id, int)):
                url = url + 'sensor__controller__sector_id={}&'.format(sensor__controller__sector_id)
        if sensor__controller__sector__workspace_id:
            if (isinstance(sensor__controller__sector__workspace_id, int)):
                url = url + 'sensor__controller__sector__workspace_id={}&'.format(sensor__controller__sector__workspace_id)
        if from_date:
            # TODO: validate date
            url = url + 'from_date={}&'.format(from_date)
        if to_date:
            # TODO: validate date
            url = url + 'to_date={}&'.format(to_date)

    response = requests.get(url, headers=headers)
    response_data = json.loads(response.content)

    results = response_data["results"]
    return results


def create_sensor_url(sensor_id):
    return GLOBAL_SERVER_SENSORS_ROUTE + str(sensor_id) + "/"


def post_sensor_raw_data(token, sensor_id, title, value):
    data = {}

    try:
        sensor_url = create_sensor_url(sensor_id)
    except Exception as e:
        raise e

    data["sensor"] = sensor_url
    data["title"] = title
    data["value"] = value

    try:
        headers = create_request_header(token)
    except Exception as e:
        raise e

    url = GLOBAL_SERVER_RAW_DATA_ROUTE
    try:
        new_data_posted = requests.post(url, headers=headers, data=data)
    except Exception as e:
        raise e
    return new_data_posted.status_code


# post_sensor_raw_data(token, 46, "ahahahah", 4)
# get_sensor_raw_data(token, to_date="2019-09-17T16:00:00")

