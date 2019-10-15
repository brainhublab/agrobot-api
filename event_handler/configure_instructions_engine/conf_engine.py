class CongfGenerator(object):
    def __init__(self, data={}):
        self.data = data

    def create_instruction(self):
        self.data["value"] += 1
        return {"[!!!]INSTRUCTION": self.data}

