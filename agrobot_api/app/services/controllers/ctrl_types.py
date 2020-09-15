import copy


class waterLevelCtrl():
    def __init__(self):
        self.topic_shema = {
            "in": {
                "valve": "/data/out/variableName",
                "level_target": "/data/out/variableName",
                "PID": {
                    "kp": "/data/out/variableName",
                    "ki": "/data/out/variableName",
                    "kd": "/data/out/variableName"
                }
            },
            "out": {
                "valve": "/data/out/valve",
                "current_level": "/data/out/waterLevel",
                "level_target": "/data/out/variableName",
                "flow_in": "/data/out/waterFlowIn",
                "flow_out": "/data/out/waterFlowOut",
                "PID": {
                    "Kp": "/data/out/pid/kp",
                    "Ki": "/data/out/pid/ki",
                    "Kd": "/data/out/pid/kd"
                }
            }
        }

    def gen_ctrl_config(self, mac):
        def_conf = copy.deepcopy(self.topic_shema)
        for each in def_conf["in"]:
            if isinstance(def_conf["in"][each], dict):
                for topic in def_conf["in"][each]:
                    def_conf["in"][each][topic] = "ctrl/" + mac + def_conf["in"][each][topic]
            else:
                def_conf["in"][each] = "ctrl/" + mac + def_conf["in"][each]

        for each in def_conf["out"]:
            if isinstance(def_conf["out"][each], dict):
                for topic in def_conf["out"][each]:
                    def_conf["out"][each][topic] = "ctrl/" + mac + def_conf["out"][each][topic]
            else:
                def_conf["out"][each] = "ctrl/" + mac + def_conf["out"][each]
        return def_conf


class lightControlCtrl():
    def __init__(self):
        self.topic_shema = {
            "in": {
               "light_mode": "/data/out/variableName",
               "target_brightness": "/data/out/variableName",
               "current_time": "/data/out/variableName",
               "clock": "/data/out/variableName",
               "light_intensity_map": "/data/out/variableName"
            },
            "out": {
                "light_mode": "/data/lightMode",
                "current_brightness": "/data/currentLightLevel",
                "target_brightness": "/data/targetLightLevel",
                "current_time": "/data/currentTime"
            }
        }

    def gen_ctrl_config(self, mac):
        def_conf = copy.deepcopy(self.topic_shema)
        for each in def_conf["in"]:
            if isinstance(def_conf["in"][each], dict):
                for topic in def_conf["in"][each]:
                    def_conf["in"][each][topic] = "ctrl/" + mac + def_conf["in"][each][topic]
            else:
                def_conf["in"][each] = "ctrl/" + mac + def_conf["in"][each]

        for each in def_conf["out"]:
            if isinstance(def_conf["out"][each], dict):
                for topic in def_conf["out"][each]:
                    def_conf["out"][each][topic] = "ctrl/" + mac + def_conf["out"][each][topic]
            else:
                def_conf["out"][each] = "ctrl/" + mac + def_conf["out"][each]
        return def_conf

    def print_light():
        print("Light Class PRint")


class ctrlTypes():
    def __init__(self):
        self.mcuClasses = {
            "waterLevel": waterLevelCtrl(),
            "lightControl": lightControlCtrl()
        }
