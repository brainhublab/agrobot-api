import sys
import os
import logging
import subprocess
import getpass
import string
import random


class GrowAutomationsStartUp(object):
    def __init__(self):
        self.api_env_path = "../.env"
        self.communication_env_path = "../.env-communication-service"
        self.access_controll_list_path = "../mosquitto/config/access_control_list.acl"
        self.mosquitto_configs_path = "../mosquitto/config/mosquitto.conf"
        self.sysLogger = self.__reg_logger()
        self.uiLogger = self.__reg_logger(type=1)

    def __reg_logger(self, type=0):
        if type == 1:
            # create logger
            logger = logging.getLogger("ui")
            logger.setLevel(logging.DEBUG)

            # create console handler and set level to debug
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            # print(type)

            formatter = logging.Formatter('%(message)s')
            ch.setFormatter(formatter)
            logger.addHandler(ch)
            return logger
        else:
            # create logger
            logger = logging.getLogger("SYS")
            logger.setLevel(logging.DEBUG)

            # create console handler and set level to debug
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)

            os.makedirs(os.path.dirname("./logs/startup.log"), exist_ok=True)
            log_reg = logging.FileHandler('./logs/startup.log', mode="w", encoding=None, delay=False)
            log_reg.setLevel(logging.DEBUG)

            # create formatter for logger output
            formatter = logging.Formatter('\n[+] - [%(levelname)s] - [%(asctime)s] - [%(name)s] - [%(message)s]')

            # add formatter to handlers
            ch.setFormatter(formatter)
            log_reg.setFormatter(formatter)

            # add handlers to logger
            logger.addHandler(ch)
            logger.addHandler(log_reg)
            return logger

    def random_str_generator(self, size=8, chars=string.ascii_uppercase + string.ascii_lowercase
                                                                        + string.digits + "!#$%&()*/=?@[]^_{}~"):
        return ''.join(random.choice(chars) for _ in range(size))

    def port_approver(self, port, used_ports):
        while port in used_ports or not port.isdecimal():
            self.uiLogger.info("[!] Bad port input or already in use!")
            self.uiLogger.info("[!] Ports already in use!--> %s\n" % used_ports)
            port = input("[~] Select another port: ")
        else:
            used_ports.append(port)
            return port

    def pwd_approver(self, info):
        while True:
            pass_var = getpass.getpass(info)
            if len(pass_var) < 8:
                self.uiLogger.info("[!] Password too short!\n")
            elif pass_var == getpass.getpass("[~] Re-type PASSWORD: "):
                return pass_var
            else:
                self.uiLogger.info("[!] Password does not match. Try again!\n")

    def usr_approver(self, usr, used_usrs):
        while usr in used_usrs or len(usr) == 0:
            self.uiLogger.info("[!] Bad username input or already in use!")
            self.uiLogger.info("[!] Usernames already in use!--> %s\n" % used_usrs)
            usr = input("[~] Select another username: ")
        else:
            used_usrs.append(usr)
            return usr

    def fill_env_files(self, opt):
        try:
            from jinja2 import Environment, FileSystemLoader
        except Exception:
            subprocess.call([sys.executable, "-m", "pip", "install", "Jinja2==2.10.3", "--user"])
        finally:
            from jinja2 import Environment, FileSystemLoader

        if opt == "0":
            POSTGRES_DB = "pgrsDB"
            POSTGRES_USER = "pgrsUSER"
            POSTGRES_PASSWORD = self.random_str_generator()
            POSTGRES_PORT = 5432
            TOKEN = self.random_str_generator(40, string.ascii_uppercase + string.ascii_lowercase
                                                                         + string.digits + ".-_")
            BROKER_PORT = 1883
            CONTROLLER_MQTT_USER = "miagiContr"
            CONTROLLER_MQTT_PASSWORD = self.random_str_generator()
            COM_MQTT_USER = "miagiCom"
            COM_MQTT_PASSWORD = self.random_str_generator()
            API_MQTT_USER = "miagiAPI"
            API_MQTT_PASSWORD = self.random_str_generator()
            UI_MQTT_USER = "miagiUI"
            UI_MQTT_PASSWORD = self.random_str_generator()

            self.uiLogger.info("[!] Variable ypu may need in configurating systems!")

            self.uiLogger.info("  POSTGRES_DB: %s" % POSTGRES_DB)
            self.uiLogger.info("  POSTGRES_USER: %s" % POSTGRES_USER)
            self.uiLogger.info("  POSTGRES_PORT: %s" % POSTGRES_PORT)
            self.uiLogger.info("  TOKEN: %s" % TOKEN)
            self.uiLogger.info("  BROKER_PORT: %s\n" % BROKER_PORT)

        else:
            used_ports = ["5000", "80"]
            used_usrs = []

            POSTGRES_DB = input("[~] Data base name: ")
            POSTGRES_USER = input("[~] Data base user: ")
            POSTGRES_PASSWORD = self.pwd_approver("[~] Data base password: ")
            POSTGRES_PORT = self.port_approver(input("[~] Data base port: "), used_ports)
            TOKEN = input("[~] API token: ")
            BROKER_PORT = self.port_approver(input("[~] Broker port: "), used_ports)
            CONTROLLER_MQTT_USER = self.usr_approver(input("[~] CONTROLLER MQTT USER: "), used_usrs)
            CONTROLLER_MQTT_PASSWORD = self.pwd_approver("[~] PASSWORD: ")
            COM_MQTT_USER = self.usr_approver(input("[~] COM MQTT USER: "), used_usrs)
            COM_MQTT_PASSWORD = self.pwd_approver("[~] PASSWORD: ")
            API_MQTT_USER = self.usr_approver(input("[~] API MQTT USER: "), used_usrs)
            API_MQTT_PASSWORD = self.pwd_approver("[~] PASSWORD: ")
            UI_MQTT_USER = self.usr_approver(input("[~] UI MQTT USER: "), used_usrs)
            UI_MQTT_PASSWORD = self.pwd_approver("[~] PASSWORD: ")

        file_loader = FileSystemLoader('templates')
        env = Environment(loader=file_loader)

        env_api_tmp = env.get_template('env_api_tmp.txt')
        env_api_content = env_api_tmp.render(POSTGRES_DB=POSTGRES_DB,
                                             POSTGRES_USER=POSTGRES_USER,
                                             POSTGRES_PASSWORD=POSTGRES_PASSWORD,
                                             POSTGRES_PORT=POSTGRES_PORT,
                                             BROKER_PORT=BROKER_PORT,
                                             API_MQTT_USER=API_MQTT_USER,
                                             API_MQTT_PASSWORD=API_MQTT_PASSWORD,
                                             TOKEN=TOKEN)

        with open(self.api_env_path, "w+") as f:
            f.write(env_api_content)
            self.sysLogger.info(" API environment created --> %s " % self.api_env_path)

        env_communication_service_tmp = env.get_template('env_communication_service_tmp.txt')
        env_com_content = env_communication_service_tmp.render(BROKER_PORT=BROKER_PORT,
                                                               TOKEN=TOKEN,
                                                               CONTROLLER_MQTT_USER=CONTROLLER_MQTT_USER,
                                                               CONTROLLER_MQTT_PASSWORD=CONTROLLER_MQTT_PASSWORD,
                                                               COM_MQTT_USER=COM_MQTT_USER,
                                                               COM_MQTT_PASSWORD=COM_MQTT_PASSWORD,
                                                               API_MQTT_USER=API_MQTT_USER,
                                                               API_MQTT_PASSWORD=API_MQTT_PASSWORD,
                                                               UI_MQTT_USER=UI_MQTT_USER,
                                                               UI_MQTT_PASSWORD=UI_MQTT_PASSWORD)
        with open(self.communication_env_path, "w+") as f:
            f.write(env_com_content)
            self.sysLogger.info(" Communication service environment created --> %s " % self.communication_env_path)

        access_control_list_tmp = env.get_template('access_control_list_tmp.txt')
        access_control_list_content = access_control_list_tmp.render(CONTROLLER_MQTT_USER=CONTROLLER_MQTT_USER,
                                                                     COM_MQTT_USER=COM_MQTT_USER,
                                                                     API_MQTT_USER=API_MQTT_USER,
                                                                     UI_MQTT_USER=UI_MQTT_USER)

        with open(self.access_controll_list_path, "w+") as f:
            f.write(access_control_list_content)
            self.sysLogger.info(" Access controll list created --> %s " % self.access_controll_list_path)

        mosquitto_conf_tmp = env.get_template('mosquitto_conf_tmp.txt')
        mosquitto_conf_content = mosquitto_conf_tmp.render(BROKER_PORT=BROKER_PORT)

        with open(self.mosquitto_configs_path, "w+") as f:
            f.write(mosquitto_conf_content)
            self.sysLogger.info(" Mosquitto config file created --> %s " % self.mosquitto_configs_path)

    def start(self):
        self.uiLogger.info("\n\n")
        self.uiLogger.info(" dP**b8 88**Yb  dP*Yb  Yb        dP 88 88b 88 "
                           "       db    88   88 888888  dP*Yb  8b    d8    db    888888 88  dP*Yb  88b 88 .dP*Y8")
        self.uiLogger.info("dP   `* 88__dP dP   Yb  Yb  db  dP  88 88Yb88 "
                           "      dPYb   88   88   88   dP   Yb 88b  d88   dPYb     88   88 dP   Yb 88Yb88 `Ybo.*")
        self.uiLogger.info("Yb  *88 88*Yb  Yb   dP   YbdPYbdP   88 88 Y88 "
                           "     dP__Yb  Y8   8P   88   Yb   dP 88YbdP88  dP__Yb    88   88 Yb   dP 88 Y88 o.`Y8b")
        self.uiLogger.info(" YboodP 88  Yb  YbodP     YP  YP    88 88  Y8 "
                           "    dP****Yb `YbodP'   88    YbodP  88 YY 88 dP====Yb   88   88  YbodP  88  Y8 8bodP'")

        self.uiLogger.info("\n\n\n\n")
        self.uiLogger.info("[*] Please select option for configuration files creation:\n")

        self.uiLogger.info("    [0][*] Auto (recommended)\n"
                           "    [1][*] Manual\n"
                           "    [2][*] Reject\n")

        opt = input("[~] Choose option(0, 1, 2): ")
        self.uiLogger.info("\n")
        if opt in ["0", "1", "2"]:
            if opt == "0" or "1":
                self.fill_env_files(opt)
            elif opt == "2":
                self.uiLogger.info("Process is rejected")
        else:
            self.uiLogger.info("[!] Bad option number choosen")


GrowAutomationsStartUp().start()
