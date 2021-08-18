from datetime import datetime
import sqlite3
from sqlite3 import Error
from playsound import playsound

def connectToDB():
    try:
        db_file = "alarms.db"
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(f"[connectToDB] Error: {e}")
    finally:
        return conn


conn = connectToDB()


cur = conn.cursor()
command = "SELECT alarmDate, type, notificationType, optionalMessage FROM alarms;"
cur.execute(command)

rows = cur.fetchall()

for row in rows:
    print(row)

    alarmTime = datetime.fromisoformat(str(row[0]))
    if alarmTime < datetime.now():
        # notify the user
        if row[2] == "speech" or row[2] == "both":
            playsound('proyectoIntegrador/doorbell-2.wav')

        print("Deleting alarm")
        command = 'DELETE FROM alarms WHERE alarmDate = ? AND type = ?'
        values = (row[0], row[1])
        cur = conn.cursor()
        cur.execute(command, values)
        conn.commit()