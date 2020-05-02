from flask import Flask, g, jsonify, abort
import sqlite3
from datetime import datetime

DATABASE = '../gateway/store_sensor_data/sensor_data.db'


app = Flask(__name__)


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route("/temps/<int:node>")
def temps(node):
    temp_row = None
    try:
        cur = get_db().cursor()

        cur.execute('SELECT temp, time, rssi FROM temps WHERE node=? ORDER BY time DESC LIMIT 1', [node])
        temp_row = cur.fetchone()

        cur.execute("SELECT AVG(temp) FROM temps WHERE node=? AND time >= DATETIME('now', '-10 minute')", [node])
        avg_last_10_mins = cur.fetchone()[0]

        cur.execute("SELECT AVG(temp) FROM temps WHERE node=? AND time >= DATETIME('now', '-70 minute') AND time < DATETIME('now', '-60 minute')", [node])
        avg_60_mins_ago = cur.fetchone()[0]

        temp_diff = avg_last_10_mins - avg_60_mins_ago

        temp_change_per_min = temp_diff / 60

        cur.close()
    except sqlite3.OperationalError:
        return jsonify(message="Database error"), 500

    if temp_row is None:
        return jsonify(message="no data for node"), 404

    return jsonify({'temp': temp_row[0], 'time': temp_row[1], 'rssi': temp_row[2], 'temp_diff_60_min': temp_diff, 'avg_temp_change_per_min_60_min': temp_change_per_min})


@app.route("/humidities/<int:node>")
def humidities(node):
    humidity_row = None
    try:
        cur = get_db().execute('SELECT humidity, time, rssi FROM humidities WHERE node=? ORDER BY time DESC LIMIT 1', [node])
        humidity_row = cur.fetchone()
        cur.close()
    except sqlite3.OperationalError:
        return jsonify(message="Database error"), 500

    if humidity_row is None:
        return jsonify(message="no data for node"), 404

    return jsonify({'humidity': humidity_row[0], 'time': humidity_row[1], 'rssi': humidity_row[2]})


@app.route("/pressures/<int:node>")
def pressures(node):
    pressure_row = None
    try:
        cur = get_db().cursor()
        cur.execute('SELECT pressure, time, rssi FROM pressures WHERE node=? ORDER BY time DESC LIMIT 1', [node])
        pressure_row = cur.fetchone()

        cur.execute("SELECT AVG(pressure) FROM pressures WHERE node=? AND time >= DATETIME('now', '-1 hour')", [node]);
        avg_last_hour = cur.fetchone()[0]

        cur.execute("SELECT AVG(pressure) FROM pressures WHERE node=? AND time >= DATETIME('now', '-13 hour') AND time < DATETIME('now', '-12 hour')", [node]);
        avg_twelve_hours_ago = cur.fetchone()[0]

        pressure_diff = avg_last_hour - avg_twelve_hours_ago

        pressure_change_per_hour = pressure_diff / 12

        cur.close()
    except sqlite3.OperationalError:
        return jsonify(message="Database error"), 500

    if pressure_row is None:
        return jsonify(message="no data for node"), 404

    return jsonify({'pressure': pressure_row[0], 'time': pressure_row[1], 'rssi': pressure_row[2], 'pressure_change_12_hour': pressure_diff, 'avg_pressure_change_per_hour_12_hour': pressure_change_per_hour})
