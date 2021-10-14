import sqlite3
import sys
import time

from soilmoisture import SoilMoistureSensor
from sunlight import SunLightSensor
from temperaturehumidity import TemperatureAndHumiditySensor
from relay import Relay
from button import DualButton

def row_to_dict(cursor: sqlite3.Cursor, row: sqlite3.Row) -> dict:
    data = {}
    for idx, col in enumerate(cursor.description):
        data[col[0]] = row[idx]
    return data

class SensorDB:
    def __init__(self, db_file: str):
        self.__db_file = db_file

        with sqlite3.connect(self.__db_file) as connection:
            table_cursor = connection.cursor()
            table_cursor.execute('''CREATE TABLE IF NOT EXISTS sensor_values 
                                    (date INTEGER PRIMARY KEY, 
                                     soil_moisture INTEGER,
                                     temperature INTEGER,
                                     humidity INTEGER,
                                     soil_temperature INTEGER,
                                     visible INTEGER,
                                     infra_red INTEGER,
                                     ultra_violet REAL,
                                     relay_state INTEGER,
                                     button1_state INTEGER,
                                     button2_state INTEGER)''')
            connection.commit()
            table_cursor.close()
    
    def save_values(self, soil_moisture_sensor: SoilMoistureSensor, temperature_humidity_sensor: TemperatureAndHumiditySensor, sunlight_sensor: SunLightSensor,
                    relay: Relay, button: DualButton) -> None:
        print('Saving sensor values...', file=sys.stdout)
        utc_time = int(time.time())

        soil_moisture = soil_moisture_sensor.moisture

        temperature = temperature_humidity_sensor.temperature
        humidity = temperature_humidity_sensor.humidity
        soil_temperature = temperature_humidity_sensor.soil_temperature
        
        visible_light = sunlight_sensor.visible
        infra_red = sunlight_sensor.infra_red
        ultra_violet = sunlight_sensor.ultra_violet

        relay_state = relay.state

        button1_state = button.button1
        button2_state = button.button2

        with sqlite3.connect(self.__db_file) as connection:
            insert_cursor = connection.cursor()
            
            insert_cursor.execute('''INSERT INTO sensor_values VALUES 
                                  (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                                  (utc_time, soil_moisture, temperature, humidity, soil_temperature, visible_light, infra_red, ultra_violet, relay_state, button1_state, button2_state))
            
            connection.commit()
            insert_cursor.close()
        
        print('Sensor values saved!', file=sys.stdout)

    def get_history(self, from_date: int) -> list:
        with sqlite3.connect(self.__db_file) as connection:
            connection.row_factory = row_to_dict
            select_cursor = connection.cursor()
            select_cursor.execute(f'SELECT * FROM sensor_values DESC WHERE date > {from_date} ORDER BY date')
            rows = select_cursor.fetchall()
            select_cursor.close()
            return rows
