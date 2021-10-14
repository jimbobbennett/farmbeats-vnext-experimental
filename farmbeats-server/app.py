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

DB_POLL_TIME = 60
db_poll_timer = threading.Thread()
db_dataLock = threading.Lock()

CACHE_POLL_TIME = 2
cache_poll_timer = threading.Thread()
cache_dataLock = threading.Lock()

@app.route('/', methods=['GET'])
def home():
    return "Hello"

@app.route('/all', methods=['GET'])
def get_all():
    return {
        'button1': dual_button.button1,
        'button2': dual_button.button2,
        'soil_moisture': soil_moisture_sensor.moisture,
        'relay': relay.state,
        'temperature': temp_sensor.temperature,
        'soil_temperature': temp_sensor.soil_temperature,
        'humidity': temp_sensor.humidity,
        'visible': sunlight_sensor.visible,
        'ultra_violet': sunlight_sensor.ultra_violet,
        'infra_red': sunlight_sensor.infra_red,
    }

@app.route('/history', methods=['GET'])
def get_all_history():
    with db_dataLock:
        from_date = request.args.get('from_date', 0)
        return json.dumps(sensor_db.get_history(from_date))

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

@app.route('/sunlight', methods=['GET'])
def sunlight_get():
    return {
        'visible': sunlight_sensor.visible,
        'IR': sunlight_sensor.infra_red,
        'UV': sunlight_sensor.ultra_violet
    }

@app.route('/temperature-humidity', methods=['GET'])
def temperature_humidity_get():
    return {
        'temperature': temp_sensor.temperature,
        'soil_temperature': temp_sensor.soil_temperature,
        'humidity': temp_sensor.humidity
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', metavar='port', type=int, default=443, help='the port to run on')

    args = parser.parse_args()

    print(f'FarmBeats server running on port {args.port}')
    
    def interrupt():
        global db_poll_timer
        global cache_poll_timer
        
        db_poll_timer.cancel()
        cache_poll_timer.cancel()

    def save_values():
        with db_dataLock:
            sensor_db.save_values(soil_moisture_sensor, temp_sensor, sunlight_sensor, relay, dual_button)

    def handle_db_poll_timer():
        global db_poll_timer
        save_values()

        db_poll_timer = threading.Timer(DB_POLL_TIME, handle_db_poll_timer, ())
        db_poll_timer.start()   

    def start_db_poll_timer():
        global db_poll_timer
        save_values()        
        
        db_poll_timer = threading.Timer(DB_POLL_TIME, handle_db_poll_timer, ())
        db_poll_timer.start()

    def capture_values():
        with cache_dataLock:
            dual_button.capture_values()
            relay.capture_values()
            soil_moisture_sensor.capture_values()
            sunlight_sensor.capture_values()
            temp_sensor.capture_values()

    def handle_cache_poll_timer():
        global cache_poll_timer
        capture_values()

        cache_poll_timer = threading.Timer(CACHE_POLL_TIME, handle_cache_poll_timer, ())
        cache_poll_timer.start()   

    def start_cache_poll_timer():
        global cache_poll_timer
        capture_values()
        
        cache_poll_timer = threading.Timer(CACHE_POLL_TIME, handle_cache_poll_timer, ())
        cache_poll_timer.start()

    start_cache_poll_timer()
    start_db_poll_timer()
    atexit.register(interrupt)

    app.run(port=args.port, host='0.0.0.0', ssl_context=('cert.pem', 'key.pem'))

if __name__ == '__main__':
    main()
