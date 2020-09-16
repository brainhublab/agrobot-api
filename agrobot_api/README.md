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

- 📦 Flask-restful
-   PostgreSQL
- 🛡 Paho-mqtt client
- 🌍 Python
-   Timescaledb


## 🔨 Usage
<p>When agrobot_api container run for first time may need to migrate db handly. Also need to extend the database with TimescaleDB </p>

```bash
# to enter agrobot_api container run this in terminal:
docker exec -it agrobot_api /bin/ash

# once you enter the container run:
flask db migrate
flask db upgrade
# in case of error check this:
  https://stackoverflow.com/questions/54055469/how-to-use-sqlalchemy-utils-in-a-sqlalchemy-model
# then exit

# check out this to extend the database with TimescaleDB:
  https://docs.timescale.com/latest/getting-started/setup

```


## 🤝 Contact

Email us at [brainhublab@gmail.com](mailto:brainhublab@gmail.com)
