#
# barrys-bitters/temp_monitor/daq.py
#

import time
import sqlite3, yaml
from w1thermsensor import W1ThermSensor, Unit

# -----------------------------------------------------
class TempSensor:
    # -----------------------------------------------------
    def __init__(self, id, name, sensor):
        self.ID = id
        self.Name = name
        self.Sensor = sensor

# -----------------------------------------------------
class TempLogger:
    # -----------------------------------------------------
    def __init__(self, config: str):
        """
        Configures data acquisition and finds sensors.
        """
        with open(config) as inFile:
            config = yaml.safe_load(inFile)

        # Find available sensors and store configuration
        w1_sensors = W1ThermSensor.get_available_sensors()
        self.sensors = {}
        for w1_sensor in w1_sensors:
            if w1_sensor.id not in config["tempmon"]["id"]:
                raise RuntimeError(f"Found unknown temperature sensor {sensor.id}.")
            else:
                print(f"Found temperature sensor {w1_sensor.id}.")
                index = config["tempmon"]["id"].index(w1_sensor.id)
                sensor = TempSensor(w1_sensor.id, config["tempmon"]["name"][index], w1_sensor)
                self.sensors[w1_sensor.id] = sensor
        for requested_id in config["tempmon"]["id"]:
            if requested_id not in self.sensors:
                raise RuntimeError(f"Requested sensor {requested_id} not found.")

        # Set up database table
        db_columns = [{"name": "timestamp", "type": "DATETIME DEFAULT CURRENT_TIMESTAMP"}]
        for sensor_id in self.sensors:
            db_columns.append({"name": f"temp_{self.sensors[sensor_id].Name}_C", "type": "REAL"})
            db_columns.append({"name": f"temp_{self.sensors[sensor_id].Name}_F", "type": "REAL"})
        sql_columns = ", ".join(f"{col['name']} {col['type']}" for col in db_columns)
        self.db = sqlite3.connect(config["tempmon"]["database"])
        cursor = self.db.cursor()
        cursor.execute(f"CREATE TABLE IF NOT EXISTS templog ({sql_columns});")
        self.db.commit()

    # -----------------------------------------------------
    def end(self):
        self.db.close()

    # -----------------------------------------------------
    def log(self, temp):
        """
        Log temperature readings to database.
        """
        data = {}
        for sensor_id in temp:
            data[f"temp_{self.sensors[sensor_id].Name}_C"] = temp[sensor_id]['C']
            data[f"temp_{self.sensors[sensor_id].Name}_F"] = temp[sensor_id]['F']

        columns = ", ".join(data.keys())
        placeholders = ", ".join("?" for _ in data)
        values = list(data.values())
        cursor = self.db.cursor()
        cursor.execute(f"INSERT INTO templog ({columns}) VALUES ({placeholders})", values)
        self.db.commit()

    # -----------------------------------------------------
    def read(self):
        """
        Read the temperature sensors.
        """
        temp = {}
        for sensor_id in self.sensors:
            temp_c = self.sensors[sensor_id].Sensor.get_temperature(Unit.DEGREES_C)
            temp_f = self.sensors[sensor_id].Sensor.get_temperature(Unit.DEGREES_F)
            temp[sensor_id] = {"C": temp_c, "F": temp_f}
        return temp

    # -----------------------------------------------------
    def run(self):
        """
        Run DAQ in loop.
        """
        while True:
            temp = self.read()
            self.log(temp)
            time.sleep(10)

# -----------------------------------------------------
if __name__ == "__main__":
    logger = TempLogger(config="../config.yaml")
    logger.run()
    logger.end()
