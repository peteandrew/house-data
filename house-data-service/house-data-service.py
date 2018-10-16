from flask import Flask
import sqlite3
from flask import g

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
    cur = get_db().execute('SELECT temp FROM temps WHERE node=? ORDER BY time DESC LIMIT 1', [node])
    temp_row = cur.fetchone()
    cur.close()
    if temp_row is None:
        return '0'
    else:
        return str(temp_row[0])

@app.route("/humidities/<int:node>")
def humidities(node):
    cur = get_db().execute('SELECT humidity FROM humidities WHERE node=? ORDER BY time DESC LIMIT 1', [node])
    humidity_row = cur.fetchone()
    cur.close()
    if humidity_row is None:
        return '0'
    else:
        return str(humidity_row[0])

@app.route("/pressures/<int:node>")
def pressures(node):
    cur = get_db().execute('SELECT pressure FROM pressures WHERE node=? ORDER BY time DESC LIMIT 1', [node])
    pressure_row = cur.fetchone()
    cur.close()
    if pressure_row is None:
        return '0'
    else:
        return str(pressure_row[0])

