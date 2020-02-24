import requests
import os
import json


class GlobalServerRequests(object):
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
        sensor_url = self._create_sensor_url()
        data = {}
        data["sensor"] = sensor_url
        data["title"] = self.data["title"]
        data["value"] = self.data["value"]

        headers = self._create_request_header()
        url = self.raw_data_url
        new_data_posted = requests.post(url, headers=headers, data=data)
        return new_data_posted.status_code


class LocalServerRequests(object):
    def __init__(self, mac_addr="macAddr", data={}):
        self.token = os.environ.get("TOKEN")
        self.mac_addr = mac_addr
        self.api_controllers_subscribers_url = os.environ.get("API_CONTROLLER_SUBSCRIBERS")
        self.api_controllers_url = os.environ.get("API_CONTROLLERS_URL")
        self.data = data

    def _create_request_header(self):
        return {'Authorization': 'Bearer {}'.format(self.token)}

    def _add_mac_addr_to_url(self, url):
        return url + self.mac_addr + "/"

    def _check_response(self, response):
        if response.status_code == 404:
            return False
        else:
            return True
    """                             REQUESTS                                 """

    def get_all_registered_controllers(self):
        headers = self._create_request_header()
        url = self.api_controllers_url
        response = requests.get(url, headers=headers)
        return response

    def post_new_controller(self):
        headers = self._create_request_header()
        url = self.api_controllers_url
        response = requests.post(url, headers=headers, json=self.data)
        return response

    def put_subscribers_by_mac(self):
        headers = self._create_request_header()
        url = self._add_mac_addr_to_url(self.api_controllers_subscribers_url)
        response = requests.put(url, headers=headers, json=self.data)
        return response
