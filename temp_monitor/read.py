#
# barrys-bitters/temp_monitor/read_db.py
#

import argparse
import sqlite3, yaml

def read_db():
    parser = argparse.ArgumentParser(prog="read_db.py",
                                     description="Simple tool to read SQlite database.")
    parser.add_argument('db_file', help="Database file to read.")
    parser.add_argument('--config', default='../config.yaml',
                        help="Configuration file containing temperature monitoring data.")
    config = parser.parse_args()

    with open(config.config, 'r') as configFile:
        bb_config = yaml.safe_load(configFile)
    columns = ['timestamp']
    for temp_sensor in bb_config["tempmon"]["name"]:
        columns.append(f"temp_{temp_sensor}_F")
    sql_columns = ", ".join(columns)
        
    conn = sqlite3.connect(config.db_file)
    cursor = conn.cursor()
    cursor.execute(f'SELECT {sql_columns} FROM templog')

    rows = cursor.fetchall()
    for row in rows:
        print(row)

if __name__ == "__main__":
    read_db()
