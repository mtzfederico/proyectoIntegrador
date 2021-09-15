from flask import Flask, request, Response
import mqttFunctions
import sqlite3
from sqlite3 import Error
from datetime import datetime

# Colors used for printing
class color:
    purple = '\033[95m'
    blue = '\033[94m'
    green = '\033[92m'
    red = '\033[91m'
    end = '\033[0m'

def connectToDB():
    try:
        db_file = "alarms.db"
        conn = sqlite3.connect(db_file, check_same_thread=False)
        return conn
    except Error as e:
        print(f"{color.red}[connectToDB] Error: {e}", color.end)
    finally:
        return conn

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

#<--------- Server Functions Start --------->

app = Flask(__name__)

@app.errorhandler(404)
def page_not_found(e):
    return "The page you are looking for can't be found", 404

@app.route("/changeColor", methods=['GET'])
def hello():
    red = request.args.get('red', default = "0.00", type = str)
    green = request.args.get('green', default = "0.00", type = str)
    blue = request.args.get('blue', default = "0.00", type = str)

    red = float(red)*255
    green = float(green)*255
    blue = float(blue)*255

    print(f"{color.red}Red:{color.end} {red}")
    print(f"{color.green}Green:{color.end} {green}")
    print(f"{color.blue}Blue:{color.end} {blue}")
    mqttFunctions.client.publish('lamp/rgb', payload=f"{red},{green},{blue}", qos=1, retain=False)

    return Response(f"Hello {red},{green},{blue}", status=200)

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
    app.run(host='0.0.0.0', port=9080, debug=True)
