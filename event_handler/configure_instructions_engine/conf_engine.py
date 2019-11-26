import os
import sys
sys.path.insert(0, os.path.abspath('..'))
from http_requests.requestss import EngineRequests


class InstructionGenerator(object):
    def __init__(self, data={}, token=None):
        self.data = data
        self.token = token

    def create_instruction(self):
        engine_request = EngineRequests(self.token, self.data)
        try:
            self.data["msg_type"] = "new_rule"
            self.data["rules"] = engine_request.get_rules_local_server()
            self.data["controllers"] = engine_request.controllers_config()
            self.data["value"] += 1
        except Exception as e:
            raise e
        return self.data
