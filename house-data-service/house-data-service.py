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
    try:
        cur = get_db().cursor()

        cur.execute('SELECT temp, time, rssi FROM temps WHERE node=? ORDER BY time DESC LIMIT 1', [node])
        temp_row = cur.fetchone()

        if temp_row is None:
            return jsonify(message="no data for node"), 404

        resp = {'temp': temp_row[0], 'time': temp_row[1], 'rssi': temp_row[2]}

        cur.execute("SELECT MIN(temp) FROM temps WHERE node=? AND time >= DATETIME('now', '-24 hour')", [node])
        min_temp_24_hour = cur.fetchone()[0]
        if min_temp_24_hour:
            resp['min_temp_24_hour'] = min_temp_24_hour

        cur.execute("SELECT MAX(temp) FROM temps WHERE node=? AND time >= DATETIME('now', '-24 hour')", [node])
        max_temp_24_hour = cur.fetchone()[0]
        if max_temp_24_hour:
            resp['max_temp_24_hour'] = max_temp_24_hour

        cur.execute("SELECT AVG(temp) FROM temps WHERE node=? AND time >= DATETIME('now', '-10 minute')", [node])
        avg_last_10_mins = cur.fetchone()[0]

        if avg_last_10_mins is None:
            cur.close()
            return jsonify(resp)

        cur.execute("SELECT AVG(temp) FROM temps WHERE node=? AND time >= DATETIME('now', '-70 minute') AND time < DATETIME('now', '-60 minute')", [node])
        avg_60_mins_ago = cur.fetchone()[0]

        cur.close()

        if avg_60_mins_ago is None:
            return jsonify(resp)

        temp_diff = avg_last_10_mins - avg_60_mins_ago
        resp['temp_diff_60_min'] = temp_diff

        temp_change_per_min = temp_diff / 60
        resp['avg_temp_change_per_min_60_min'] = temp_change_per_min

        return jsonify(resp)

    except sqlite3.OperationalError:
        return jsonify(message="Database error"), 500


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
    try:
        cur = get_db().cursor()
        cur.execute('SELECT pressure, time, rssi FROM pressures WHERE node=? ORDER BY time DESC LIMIT 1', [node])
        pressure_row = cur.fetchone()
        if pressure_row is None:
            return jsonify(message="no data for node"), 404

        resp = {'pressure': pressure_row[0], 'time': pressure_row[1], 'rssi': pressure_row[2]}

        cur.execute("SELECT AVG(pressure) FROM pressures WHERE node=? AND time >= DATETIME('now', '-1 hour')", [node]);
        avg_last_hour = cur.fetchone()[0]
        if avg_last_hour is None:
            return jsonify(resp)

        cur.execute("SELECT AVG(pressure) FROM pressures WHERE node=? AND time >= DATETIME('now', '-13 hour') AND time < DATETIME('now', '-12 hour')", [node]);
        avg_twelve_hours_ago = cur.fetchone()[0]
        if avg_twelve_hours_ago is None:
            return jsonify(resp)

        pressure_diff = avg_last_hour - avg_twelve_hours_ago
        resp['pressure_change_12_hour'] = pressure_diff

        pressure_change_per_hour = pressure_diff / 12
        resp['avg_pressure_change_per_hour_12_hour'] = pressure_change_per_hour

        cur.close()

        return jsonify(resp)
    except sqlite3.OperationalError:
        return jsonify(message="Database error"), 500
