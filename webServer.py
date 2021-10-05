"""
    webServer.py

    This is the web server that let's the iOS app interact with the DB and with MQTT devices.
    It needs to always be running for the app to work properly.
"""

from flask import Flask, request, Response
import json
import mqttFunctions
import sqlite3
from sqlite3 import Error
from datetime import datetime
import random
import weatherForecast

# Colors used for printing
class color:
    purple = '\033[95m'
    blue = '\033[94m'
    green = '\033[92m'
    red = '\033[91m'
    end = '\033[0m'

# Connects to the DB
def connectToDB():
    try:
        db_file = "alarms.db"
        conn = sqlite3.connect(db_file, check_same_thread=False)
        return conn
    except Error as e:
        print(f"{color.red}[connectToDB] Error: {e}", color.end)
    finally:
        return conn

# Creates the alarms table in the DB if it doesn't exist
def createTable(conn):
    sqlTable = """CREATE TABLE IF NOT EXISTS alarms (
                                        id integer PRIMARY KEY,
                                        type text NOT NULL,
                                        notificationType text NOT NULL,
                                        optionalMessage text,
                                        creationDate text NOT NULL,
                                        alarmDate text NOT NULL
                                    );"""

    try:
        c = conn.cursor()
        c.execute(sqlTable)
    except Error as e:
        print(f"{color.red}[createTable] Error:{color.end} {e}")

conn = connectToDB()
createTable(conn)

# Saves an alarm to the database. Returns True if saved, False otherwise
def addToDB(type, notificationType, optionalMessage, alarmDate):
    # notificationType puede ser speech, notification, both
    if conn == None:
        connectToDB()

    try:
        # Convert the date to text in the ISO-8601 format
        creationDate = datetime.now().isoformat()

        # Save the data to sqlite
        command = "INSERT INTO alarms(type, notificationType, optionalMessage, creationDate, alarmDate) VALUES(?, ?, ?, ?, ?)"
        values = (type, notificationType, optionalMessage, creationDate, alarmDate) # alarmDate: 2021-09-14T18:20:58.552473
        cur = conn.cursor()
        cur.execute(command, values)
        conn.commit()

    except Exception as e:
        print(f"{color.red}[addToDB] Error:{color.end} {e}")
        return False
    finally:
        print("Saved2")
        return True

def mqttServerCallback(payload):
    print("mqttServerCallback Called")
    data = payload.split(',')
    addToDB(data[0], data[1], data[2], data[3])

mqttFunctions.serverReceivedCallback = mqttServerCallback

# Generates a WEB response from a status code and some JSON
def genReturn(response_raw, status, cache='private', mimetype='application/json'):
    response = json.dumps(response_raw)
    resp = Response(response, status=status, mimetype=mimetype)
    if cache == 'private':
        resp.headers['cache-control'] = 'private'
    if cache == 'no-cache':
        resp.headers['cache-control'] = 'no-cache'
    if cache == '5min':
        resp.headers['cache-control'] = 'max-age=300' # the cache is valid for 5 minutes
    if cache == '10min':
        resp.headers['cache-control'] = 'max-age=600' # the cache is valid for 5 minutes
    return resp

#<--------- Server Functions Start --------->

app = Flask(__name__)

# Handles the pages not found
@app.errorhandler(404)
def page_not_found(e):
    return "The page you are looking for can't be found", 404

# Handles the get room status endpoint
@app.route("/getRoomStatus", methods=['GET'])
def getRoomStatus():

    outdoorTemp = weatherForecast.getTemp()

    response_raw = { "roomTemp": random.randint(5, 30), "outdoorTemp": outdoorTemp, "doorIsClosed": False } 
    status = 200

    return genReturn(response_raw, status)

# Handles the get get alarms endpoint
@app.route("/getAlarms", methods=['GET'])
def getAlarms():
    type = request.args.get('type', default = "", type = str)

    if type == "":
        return Response("Bad Request", status=300)

    cur = conn.cursor()
    command = "SELECT alarmDate, optionalMessage FROM alarms WHERE type = ? ORDER BY alarmDate DESC;"
    values = (type,)
    cur.execute(command, values)

    alarms = cur.fetchall()
    if len(alarms) <= 0:
        print("No alarms found")
        response_raw = { "alarms": [] } 
        status = 220
        return genReturn(response_raw, status)

    alarms = []

    for alarm in alarms:
        # print(alarm)

        alarmTime = datetime.fromisoformat(str(alarm[0]))

        alarmJSON = {"alarmDate": alarmTime.timestamp(), "optionalMessage": alarm[1]}
        alarms.append(alarmJSON)

    response_raw = { "alarms": alarms } 
    status = 200

    print(f"response_raw: {response_raw}")
    return genReturn(response_raw, status)

# Handles the get change color endpoint
@app.route("/changeColor", methods=['GET'])
def hello():
    red = request.args.get('red', default = "0.00", type = str)
    green = request.args.get('green', default = "0.00", type = str)
    blue = request.args.get('blue', default = "0.00", type = str)
    id = request.args.get('id', default = "", type = str)

    print(f"{color.purple}ID:{color.end} {id}")
    print(f"{color.red}Red:{color.end} {red}")
    print(f"{color.green}Green:{color.end} {green}")
    print(f"{color.blue}Blue:{color.end} {blue}")

    mqttFunctions.changeLightColor(red, green, blue, id)

    return Response(f"ID {id}: {red},{green},{blue}", status=200)

# Handles the get set alarm endpoint
@app.route("/setAlarm", methods=['POST'])
def setAlarm():
    type = request.form.get('type', default = "", type = str)
    notificationType = request.form.get('notificationType', default = "", type = str)
    alarmDate = request.form.get('date', default = "", type = str)
    optionalMessage = request.form.get('optionalMessage', default = "", type = str)

    if type != "" and notificationType != "" and alarmDate != "":
        print(f"type: {type}, date: {alarmDate}")
        
        addToDB(type, notificationType, optionalMessage, datetime.fromtimestamp(float(alarmDate)).isoformat())

        return Response(f"received {type}", status=200)

    else:
        return Response("No data received", status=300)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=9090, debug=True)
