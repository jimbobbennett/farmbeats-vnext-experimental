import sqlite3
import sys
import time

from soilmoisture import SoilMoistureSensor
from sunlight import SunLightSensor
from temperaturehumidity import TemperatureAndHumiditySensor

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
            table_cursor.execute('CREATE TABLE IF NOT EXISTS soil_moisture (date INTEGER, moisture INTEGER)')
            table_cursor.execute('CREATE TABLE IF NOT EXISTS temperature_humidity (date INTEGER, temperature INTEGER, humidity INTEGER, soil_temperature INTEGER)')
            table_cursor.execute('CREATE TABLE IF NOT EXISTS sunlight (date INTEGER, visible INTEGER, infra_red INTEGER, ultra_voilet REAL)')
            connection.commit()
            table_cursor.close()
    
    def save_values(self, soil_moisture_sensor: SoilMoistureSensor, temperature_humidity_sensor: TemperatureAndHumiditySensor, sunlight_sensor: SunLightSensor):
        print('Saving sensor values...', file=sys.stdout)
        utc_time = int(time.time())

        soil_moisture = soil_moisture_sensor.moisture

        temperature = temperature_humidity_sensor.temperature
        humidity = temperature_humidity_sensor.humidity
        soil_temperature = temperature_humidity_sensor.soil_temperature
        
        visible_light = sunlight_sensor.visible
        infra_red = sunlight_sensor.infra_red
        ultra_voilet = sunlight_sensor.ultra_voilet

        with sqlite3.connect(self.__db_file) as connection:
            insert_cursor = connection.cursor()
            
            insert_cursor.execute('INSERT INTO soil_moisture VALUES (?, ?)', (utc_time, soil_moisture))
            insert_cursor.execute('INSERT INTO temperature_humidity VALUES (?, ?, ?, ?)', (utc_time, temperature, humidity, soil_temperature))
            insert_cursor.execute('INSERT INTO sunlight VALUES (?, ?, ?, ?)', (utc_time, visible_light, infra_red, ultra_voilet))
            
            connection.commit()
            insert_cursor.close()
        
        print('Sensor values saved!', file=sys.stdout)

    def __get_history(self, table: str, from_date: int) -> list:
        with sqlite3.connect(self.__db_file) as connection:
            connection.row_factory = row_to_dict
            select_cursor = connection.cursor()
            select_cursor.execute(f'SELECT * FROM {table} WHERE date > {from_date}')
            rows = select_cursor.fetchall()
            select_cursor.close()
            return rows

    def get_soil_moisture_history(self, from_date: int) -> list:
        return self.__get_history('soil_moisture', from_date)

    def get_temperature_humidity_history(self, from_date: int) -> list:
        return self.__get_history('temperature_humidity', from_date)

    def get_sunlight_history(self, from_date: int) -> list:
        return self.__get_history('sunlight', from_date)