types = {"waterLevel": {"valve": "/data/out/valve",
                        "current_level": "/data/out/waterLevel",
                        "level_target": "/data/out/variableName",
                        "flow_in": "/data/out/waterFlowIn",
                        "flow_out": "/data/out/waterFlowOut",
                        "PID": {
                            "Kp": "/data/out/pid/kp",
                            "Ki": "/data/out/pid/ki",
                            "Kd": "/data/out/pid/kd"
                                }
                        },
         "lightControl": {"light_mode": "/data/lightMode",
                          "current_brightness": "/data/currentLightLevel",
                          "target_brightness": "/data/targetLightLevel",
                          "current_time": "/data/currentTime"
                          }
         }
