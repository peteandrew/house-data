from flask import Flask
import sqlite3
from flask import g
from datetime import datetime

DATABASE = '../gateway/sensor_data.db'


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
        cur = get_db().execute('SELECT temp, time FROM temps WHERE node=? ORDER BY time DESC LIMIT 1', [node])
        temp_row = cur.fetchone()
        cur.close()
    except sqlite3.OperationalError:
        return '-200'

    if temp_row is None:
        return '-100'
    else:
        dt = datetime.strptime(temp_row[1], '%Y-%m-%d %H:%M:%S')
        dt_now = datetime.now()
        diff = dt_now - dt
        app.logger.info(diff.seconds)
        if diff.seconds > 300:
            return '-100'
        return str(temp_row[0])


@app.route("/humidities/<int:node>")
def humidities(node):
    humidity_row = None
    try:
        cur = get_db().execute('SELECT humidity FROM humidities WHERE node=? ORDER BY time DESC LIMIT 1', [node])
        humidity_row = cur.fetchone()
        cur.close()
    except sqlite3.OperationalError:
        return '-200'

    if humidity_row is None:
        return '0'
    else:
        return str(humidity_row[0])


@app.route("/pressures/<int:node>")
def pressures(node):
    pressure_row = None
    try:
        cur = get_db().execute('SELECT pressure FROM pressures WHERE node=? ORDER BY time DESC LIMIT 1', [node])
        pressure_row = cur.fetchone()
        cur.close()
    except sqlite3.OperationalError:
        return '-200'

    if pressure_row is None:
        return '0'
    else:
        return str(pressure_row[0])

