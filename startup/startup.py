import sys
import os
import logging
import subprocess
import getpass


class GrowAutomationsStartUp(object):
    def __init__(self):
        self.api_env_path = "../.env"
        self.communication_env_path = "../.env-communication-service"
        self.cert_folder = "../certs/"
        self.access_controll_list_path = "../mosquitto/config/access_control_list.acl"
        self.mosquitto_configs_path = "../mosquitto/config/mosquitto.conf"
        self.docker_compose_path = "../docker-compose.yml"
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

    def fill_env_files(self):
        try:
            from jinja2 import Environment, FileSystemLoader
        except Exception:
            subprocess.call([sys.executable, "-m", "pip", "install", "Jinja2==2.10.3", "--user"])
        finally:
            from jinja2 import Environment, FileSystemLoader

        POSTGRES_DB = input("[~] Data base name: ")
        POSTGRES_USER = input("[~] Data base user: ")
        POSTGRES_PASSWORD = getpass.getpass("[~] Data base password: ")
        POSTGRES_HOST = input("[~] Data base host: ")

        BROKER_PORT = input("[~] Broker port: ")

        TOKEN = input("[~] Global API token: ")

        CONTROLLER_MQTT_USER = input("[~] CONTROLLER MQTT USER: ")
        CONTROLLER_MQTT_PASSWORD = getpass.getpass("[~] PASSWORD: ")

        COM_MQTT_USER = input("[~] COM MQTT USER: ")
        COM_MQTT_PASSWORD = getpass.getpass("[~] PASSWORD: ")

        EH_MQTT_USER = input("[~] EH MQTT USER: ")
        EH_MQTT_PASSWORD = getpass.getpass("[~] CONTROLLER MQTT PASSWORD: ")

        API_MQTT_USER = input("[~] API MQTT USER: ")
        API_MQTT_PASSWORD = getpass.getpass("[~] CONTROLLER MQTT PASSWORD: ")

        file_loader = FileSystemLoader('templates')
        env = Environment(loader=file_loader)

        env_api_tmp = env.get_template('env_api_tmp.txt')
        api_env_content = env_api_tmp.render(POSTGRES_DB=POSTGRES_DB,
                                             POSTGRES_USER=POSTGRES_USER,
                                             POSTGRES_PASSWORD=POSTGRES_PASSWORD,
                                             POSTGRES_HOST=POSTGRES_HOST,
                                             BROKER_PORT=BROKER_PORT,
                                             API_MQTT_USER=API_MQTT_USER,
                                             API_MQTT_PASSWORD=API_MQTT_PASSWORD,
                                             TOKEN=TOKEN)

        with open(self.api_env_path, "w+") as f:
            f.write(api_env_content)
            self.sysLogger.info("API environment created!")

        env_communication_service_tmp = env.get_template('env_communication_service_tmp.txt')
        com_env_content = env_communication_service_tmp.render(BROKER_PORT=BROKER_PORT,
                                                               TOKEN=TOKEN,
                                                               CONTROLLER_MQTT_USER=CONTROLLER_MQTT_USER,
                                                               CONTROLLER_MQTT_PASSWORD=CONTROLLER_MQTT_PASSWORD,
                                                               COM_MQTT_USER=COM_MQTT_USER,
                                                               COM_MQTT_PASSWORD=COM_MQTT_PASSWORD,
                                                               EH_MQTT_USER=EH_MQTT_USER,
                                                               EH_MQTT_PASSWORD=EH_MQTT_PASSWORD,
                                                               API_MQTT_USER=API_MQTT_USER,
                                                               API_MQTT_PASSWORD=API_MQTT_PASSWORD)
        with open(self.communication_env_path, "w+") as f:
            f.write(com_env_content)
            self.sysLogger.info("Communication environment created!")

        access_control_list_tmp = env.get_template('access_control_list_tmp.txt')
        access_control_list_content = access_control_list_tmp.render(CONTROLLER_MQTT_USER=CONTROLLER_MQTT_USER,
                                                                     COM_MQTT_USER=COM_MQTT_USER,
                                                                     EH_MQTT_USER=EH_MQTT_USER,
                                                                     API_MQTT_USER=API_MQTT_USER)

        with open(self.access_controll_list_path, "w+") as f:
            f.write(access_control_list_content)
            self.sysLogger.info("Access controll list created!")

        mosquitto_conf_tmp = env.get_template('mosquitto_conf_tmp.txt')
        mosquitto_conf_content = mosquitto_conf_tmp.render(BROKER_PORT=BROKER_PORT)

        with open(self.mosquitto_configs_path, "w+") as f:
            f.write(mosquitto_conf_content)
            self.sysLogger.info("Mosquitto config file created!")

        docker_compose_tmp = env.get_template('docker_compose_tmp.txt')
        docker_compose_content = docker_compose_tmp.render(BROKER_PORT=BROKER_PORT)

        with open(self.docker_compose_path, "w+") as f:
            f.write(docker_compose_content)
            self.sysLogger.info("docker-compose file created!")

    def create_certs(self):
        self.sysLogger.info("To create certificates please install ")
        try:
            openssl_install_cmd = "sudo apt-get install openssl"
            openssl_install_cmd = "sudo pacman -S openssl"
            subprocess.call(openssl_install_cmd, shell=True)
        except Exception:
            self.sysLogger.info("Fail to install 'openssl'!\n Error: {}".format(e))

        self.uiLogger.info("Start creating certficates for!")
        self.uiLogger.info("Need to fill in some data!")
        self.uiLogger.info("\n\n")

        # [1]
        ca_key_cmd = "openssl genrsa -des3 -out {}ca.key 2048".format(self.cert_folder)
        subprocess.call(ca_key_cmd, shell=True)
        self.sysLogger.info("CA key pair - [created]!")

        # [2]
        self.sysLogger.info("Don't password protect!!!")
        ca_crt_cmd = ("openssl req -new -x509 -days 1826 -key {0}ca.key "
                      "-out {0}ca.crt").format(self.cert_folder)
        subprocess.call(ca_crt_cmd, shell=True)
        self.sysLogger.info("CA certificate - [created]")

        # [3]
        server_key_cmd = ("openssl genrsa -out "
                          "{}server.key 2048").format(self.cert_folder)
        subprocess.call(server_key_cmd, shell=True)
        self.sysLogger.info("Broker key pair - [created]")

        # [4]
        self.sysLogger.info("Set 'common name' to be IP publick IP addres!!! "
                            "/for development (set ip addres of machine il localhost)/")
        self.sysLogger.info("Don't password protect!!!")
        server_csr_cmd = ("openssl req -new -out {0}server.csr "
                          "-key {0}server.key").format(self.cert_folder)
        subprocess.call(server_csr_cmd, shell=True)
        self.sysLogger.info("Broker certificate - [created]")

        # [5]
        server_crt_cmd = ("openssl x509 -req -in {0}server.csr -CA {0}ca.crt "
                          "-CAkey {0}ca.key -CAcreateserial -out {0}server.crt "
                          "-days 36000").format(self.cert_folder)
        subprocess.call(server_crt_cmd, shell=True)
        self.sysLogger.info("Signed broker certificate - [created]")

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
        self.uiLogger.info("[1][*] Fill in the configuration information\n"
                           "[2][*] Create mosquitto certificates.")
        self.uiLogger.info("\n\n")

        opt = input("[~] Choose number of option: ")

        if opt in ["1", "2", "3"]:
            # TODO: check / install openssllocal net jinja2
            if opt == "1":
                self.fill_env_files()
            elif opt == "2":
                self.create_certs()
        else:
            self.uiLogger.info("[!] Bad option number choosen")


GrowAutomationsStartUp().start()
