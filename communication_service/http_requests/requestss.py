import requests
import os


class LocalServerRequests(object):

    def __init__(self, token, data):
        self.token = token
        self.raw_data_url = os.environ.get("GLOBAL_SERVER_RAW_DATA_ROUTE")
        self.sensors_url = os.environ.get("GLOBAL_SERVER_SENSORS_ROUTE")
        self.data = data

    def _create_request_header(self):
        return {'Authorization': 'Bearer {}'.format(self.token)}

    def _create_sensor_url(self):
        return self.sensors_url + str(self.data["sensor_id"]) + "/"

    def post_sensor_raw_data(self):
        data = {}

        try:
            sensor_url = self._create_sensor_url()
        except Exception as e:
            raise e

        data["sensor"] = sensor_url
        data["title"] = self.data["title"]
        data["value"] = self.data["value"]

        try:
            headers = self._create_request_header()
        except Exception as e:
            raise e

        # self.raw_data_url must be route for raw data
        url = self.raw_data_url
        try:
            new_data_posted = requests.post(url, headers=headers, data=data)
        except Exception as e:
            raise e
        return new_data_posted.status_code

