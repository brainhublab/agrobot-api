import requests
import os


class LocalServerRequests(object):
    def __init__(self, mac_addr="macAddr", data={}):
        self.token = os.environ.get("TOKEN")
        self.mac_addr = mac_addr
        self.api_controllers_url = os.environ.get("API_CONTROLLERS_URL")
        self.api_ctrl_conf = os.environ.get("API_CTRL_CONF_GET")
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

    def send_conf_trigger(self):
        headers = self._create_request_header()
        url = self._add_mac_addr_to_url(self.api_ctrl_conf)
        response = requests.get(url, headers=headers)
        return response

    def post_new_controller(self):
        headers = self._create_request_header()
        url = self.api_controllers_url
        response = requests.post(url, headers=headers, json=self.data)
        return response
