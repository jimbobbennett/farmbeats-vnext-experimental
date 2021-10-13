import argparse
import atexit
import json
import threading
from flask import Flask, request
from flask_cors import CORS

from button import DualButton
from relay import Relay
from sensor_db import SensorDB
from soilmoisture import SoilMoistureSensor
from sunlight import SunLightSensor
from temperaturehumidity import TemperatureAndHumiditySensor

app = Flask(__name__)
CORS(app)

dual_button = DualButton(18)
relay = Relay(22)
soil_moisture_sensor = SoilMoistureSensor(0)
sunlight_sensor = SunLightSensor()
temp_sensor = TemperatureAndHumiditySensor(16, 5)

sensor_db = SensorDB('farmbeats.db')

SENSOR_POLL_TIME = 60
poll_timer = threading.Thread()
dataLock = threading.Lock()

@app.route('/button', methods=['GET'])
def button_get():
    return {
        'button1': dual_button.button1,
        'button2': dual_button.button2
    }

@app.route('/relay', methods=['POST'])
def relay_post():
    body = request.json
    if 'value' in body:
        if body['value']:
            relay.on()
        else:
            relay.off()

        return 'OK', 200

    return 'Invalid payload', 400

@app.route('/relay', methods=['GET'])
def relay_get():
    return {
        'value': relay.state
    }

@app.route('/soil-moisture', methods=['GET'])
def soil_moisture_get():
    return {
        'value': soil_moisture_sensor.moisture
    }

@app.route('/history/soil-moisture', methods=['GET'])
def soil_moisture_history_get():
    from_date = request.args.get('from_date', 0)
    return json.dumps(sensor_db.get_soil_moisture_history(from_date))

@app.route('/sunlight', methods=['GET'])
def sunlight_get():
    return {
        'visible': sunlight_sensor.visible,
        'IR': sunlight_sensor.infra_red,
        'UV': sunlight_sensor.ultra_voilet
    }

@app.route('/history/sunlight', methods=['GET'])
def sunlight_history_get():
    from_date = request.args.get('from_date', 0)
    return json.dumps(sensor_db.get_sunlight_history(from_date))

@app.route('/temperature-humidity', methods=['GET'])
def temperature_humidity_get():
    return {
        'temperature': temp_sensor.temperature,
        'soil_temperature': temp_sensor.soil_temperature,
        'humidity': temp_sensor.humidity
    }

@app.route('/history/temperature-humidity', methods=['GET'])
def temperature_humidity_history_get():
    from_date = request.args.get('from_date', 0)
    return json.dumps(sensor_db.get_temperature_humidity_history(from_date))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', metavar='port', type=int, default=443, help='the port to run on')

    args = parser.parse_args()

    print(f'FarmBeats server running on port {args.port}')
    
    def interrupt():
        global poll_timer
        poll_timer.cancel()

    def handle_poll_timer():
        global poll_timer
        with dataLock:
            sensor_db.save_values(soil_moisture_sensor, temp_sensor, sunlight_sensor)

        poll_timer = threading.Timer(SENSOR_POLL_TIME, handle_poll_timer, ())
        poll_timer.start()   

    def start_poll_timer():
        global poll_timer
        with dataLock:
            sensor_db.save_values(soil_moisture_sensor, temp_sensor, sunlight_sensor)
        
        poll_timer = threading.Timer(SENSOR_POLL_TIME, handle_poll_timer, ())
        poll_timer.start()

    start_poll_timer()
    atexit.register(interrupt)

    app.run(port=args.port, host='0.0.0.0', ssl_context='adhoc')

if __name__ == '__main__':
    main()
