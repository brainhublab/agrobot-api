<div align="center">
  <a>
    <img width="230" src="./images/plant.jpg">
  </a>
</div>
<div align="center">
  <h1>Agrobot Api</h1>
  <p>Server side implementation for automation agricultor processes </p>
  <!--
  optional images (remove <-- arrows and use this layout if you need)

  <p align="middle">
    <img height="160" src="./images/cbm.jpg">
    <img height="160" src="./images/earth.png">
    <img height="160" src="./images/nature.png">
  </p>
  -->
</div>

## ✨ Features / Tech stack
-   Communicate with hardware parts, store data and manage configurations
- 📦 Docker
- 📦 Docker-compose
- 🌍 Python
- 🛡 Eclipse Mosquitto broker
- 🛡 Paho-mqtt client

## 📦 Install
0. Clone the project
1. Enter project directory
    ```
    cd project directory
    ```
2. Create .env file and mosquitto configs
    - run startup program (python v3)
    ```
    python /startup/startup.py
    ```
    - choose option '0' to autogenerate conf and env files
      - /.env
      - /mosquitto/config/access_control_list.acl
      - /mosquitto/config/mosquitto.conf
      
3. Build images in docker compose:
    ```
    docker-compose build
    ```
4. Run images:
    ```
    docker-compose up
    ```
5. Go to `agrobot_api/README.md` for DB setup instructions

## Usage
1. View :
    - `tests/localhost_tests`(implement controller funcs)
    - `tests/insomnia.json`(exported insomnia requests)
    - `ControllerClientTopicShema.txt`(user - topic rules)

## 🤝 Contact

Email us at [brainhublab@gmail.com](mailto:brainhublab@gmail.com)
