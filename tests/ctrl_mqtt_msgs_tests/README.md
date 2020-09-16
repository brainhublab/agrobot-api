<p>Test Controller funcs</p>


## ✨ Features / Tech stack
- 🛡 Paho-mqtt client
- 🌍 Python


## 🔨 Usage
<p>When system is up mqtt_master_cli start listen authentication topic for new controller to registrate (can test with new_ctrl.py).
This will create controller object in DB with config for its own type. </p>

<p>ctrl_data_pub.py publish data in topic to mqtt_master. If controller exist will create Timescaledb hypertable (if not exist already) and row with data in it. Also mqtt will send data to UI in topic for that</p>

<p>ctrl_log_pub.py publish log in topic to mqtt_master. For now just collect the wog and send it to UI</p>

<p>ctrl_health_pub.py publish health condition (baterry life, connection condition, etc.) in topic to mqtt_master. For now just send it to UI</p>


## 🤝 Contact

Email us at [brainhublab@gmail.com](mailto:brainhublab@gmail.com)
