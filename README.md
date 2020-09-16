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

```bash
# clone the project

cd <project-folder>
docker-compose build
```

## 🔨 Usage

```bash
docker-compose up
# view README in agrobot_api directory
# view test_scripts/localhost_tests
# view topic shema in ControllerClientTopicShema.txt
```

## ⌨️ Development

```bash
export ENV=development
docker-compose up
```


## 🤝 Contact

Email us at [brainhublab@gmail.com](mailto:brainhublab@gmail.com)
