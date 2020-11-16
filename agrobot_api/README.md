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


## 🔨 Install
<p>When agrobot api container run for first time you may need to migrate db handly. Also you will need to extend the database with TimescaleDB </p>

0. Migrate DB tables:
      - Enter api container:
        ```
        docker exec -it agrobot_api /bin/ash
        ```
      - Migrarate DB tables:
          ```
          flask db migrate
          ```
      - Upgrade DB tables:
          ```
          flask db upgrade
          ```
      !!! In case of `sqlalchemy-utils` error check [this](https://stackoverflow.com/questions/54055469/how-to-use-sqlalchemy-utils-in-a-sqlalchemy-model):

1. Extend PostgreSQL with TimescaleDB view [this](https://docs.timescale.com/latest/getting-started/setup):


## 🤝 Contact

Email us at [brainhublab@gmail.com](mailto:brainhublab@gmail.com)
