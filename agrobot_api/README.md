<div align="center">
  <h1>Api</h1>
  <p>Flask restful api implementation for agrobot</p>
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
-   Flask
- 📦 Flask-restful
- 🌍 Python
- 🛡 Paho-mqtt client
-   Nginx
-   PostgreSQL
- 📦 SQLAlchemy
-   TimescaleDB


## 🔨 Usage
<p>When agrobot_api container run for first time may need to migrate db handly. Also need to extend the database with TimescaleDB </p>

0. Migrate DB tables:
      - Enter api container:
        ```bash
        docker exec -it agrobot_api /bin/ash
        ```
      - Migrarate DB tables:
          ```bash
          flask db migrate
          ```
      - Create a super user:
          ```bash
          flask db upgrade
          ```
      !!! In case of sqlalchemy-utils error check [this](https://stackoverflow.com/questions/54055469/how-to-use-sqlalchemy-utils-in-a-sqlalchemy-model):

1. Extend PostgreSQL with TimescaleDB view [this](https://docs.timescale.com/latest/getting-started/setup):


## 🤝 Contact

Email us at [brainhublab@gmail.com](mailto:brainhublab@gmail.com)
