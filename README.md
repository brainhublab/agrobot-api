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
    ```bash
    cd project directory
    ```
2. Build images in docker compose:
    ```bash
    docker-compose build
    ```
3. Run images:
    ```bash
    docker-compose up
    ```
4. Go to `agrobot_api/README.md` for DB setup instructions

5. View :
    - `tests/localhost_tests`(implement controller funcs)
    - `tests/insomnia.json`(exported insomnia requests)
    - `ControllerClientTopicShema.txt`(user - topic rules)

## 🤝 Contact

Email us at [brainhublab@gmail.com](mailto:brainhublab@gmail.com)
