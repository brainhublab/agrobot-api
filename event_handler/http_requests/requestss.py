import requests
import os
import json


class EngineRequests(object):

    def __init__(self, token, data):
        self.token = token
        self.g_raw_data_url = os.environ.get("GLOBAL_SERVER_RAW_DATA_ROUTE")
        self.g_sensors_url = os.environ.get("GLOBAL_SERVER_SENSORS_ROUTE")

        self.local_controller_config_url = os.environ.get("LOCAL_SERVER_CONTROLLERS_CONFIGURATIONS")
        self.local_automation_rules_url = os.environ.get("LOCAL_SERVER_AUTOMATION_RULES")

        self.data = data

    def _create_request_header(self):
        return {'Authorization': 'Bearer {}'.format(self.token)}

    def _create_sensor_url(self):
        return self.g_sensors_url + str(self.data["sensor_id"]) + "/"

    def _check_response(self, response):
        if response.status_code == 404:
            return False
        else:
            return True

    def get_rules_local_server(self):
        url = self.local_automation_rules_url

        response = requests.get(url)
        if self._check_response(response):
            response_data = json.loads(response.content)
            return response_data
        else:
            response_data = None
            return response_data

    def controllers_config(self, obj_id=None,):
        url = self.local_controller_config_url

        if obj_id:
            if (isinstance(obj_id, int)):
                url += '{}/'.format(obj_id)

                response = requests.get(url)
                if self._check_response(response):
                    response_data = json.loads(response.content)
                    return response_data
                else:
                    response_data = None
                    return response_data
        else:
            response = requests.get(url)
            if self._check_response(response):
                response_data = json.loads(response.content)
                return response_data
            else:
                response_data = None
                return response_data


    def get_g_sensor_raw_data(self,
                              obj_id=None,
                              sensor_id=None,
                              sensor__sensor_type_id=None,
                              sensor__controller_id=None,
                              sensor__controller__sector_id=None,
                              sensor__controller__sector__workspace_id=None,
                              from_date=None,
                              to_date=None):

        headers = self._create_request_header()
        url = self.g_raw_data_url
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

