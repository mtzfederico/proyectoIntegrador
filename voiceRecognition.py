import speech_recognition as sr
# from word2number import w2n
from datetime import datetime
from datetime import timedelta
import sqlite3
from sqlite3 import Error
import pyowm
import credentials

openMap = pyowm.OWM(credentials.openWeatherMapsAPIKey)
weatherManager = openMap.weather_manager()

def connectToDB():
    try:
        db_file = "alarms.db"
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(f"[connectToDB] Error: {e}")
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
        print(e)

conn = connectToDB()
createTable(conn)

def addToDB(type, notificationType, optionalMessage, alarmDate):
    # notificationType puede ser speech, notification, both
    if conn == None:
        connectToDB()

    try:
        creationDate = datetime.now().isoformat()

        command = "INSERT INTO alarms(type, notificationType, optionalMessage, creationDate, alarmDate) VALUES(?, ?, ?, ?, ?)"
        values = (type, notificationType, optionalMessage, creationDate, alarmDate)
        cur = conn.cursor()
        cur.execute(command, values)
        conn.commit()

    except Exception as e:
        print(f"[addToDB] Error: {e}")
    finally:
        print("Saved")
    

def processReminderDetails(googleString):
    q = googleString.lower().split("remind me in ")[1]
    timeUnit = q.split(" ")[1]

    time = q.split(f" {timeUnit}")[0]
    print(f"time: {time}")

    now = datetime.now()
    if timeUnit == "minutes":
        alarmTime = now + timedelta(minutes=int(time))
    elif timeUnit == "seconds":
        alarmTime = now + timedelta(seconds=int(time))
    elif timeUnit == "hours":
        alarmTime = now + timedelta(hours=int(time))
    elif timeUnit == "days":
        alarmTime = now + timedelta(days=int(time))

    print(f"timeUnit: {timeUnit}")

    description = q.split(" ")[2:]
    description = ' '.join(description)
    print(f"description: {description}")

    print(f"alarmTime: {alarmTime}")

    addToDB("reminder", "speech", "", alarmTime)
    return True

weekDays = {"monday": "0", "tuesday": "1", "wednesday": "2", "thursday": "3", "friday": "4", "saturday": "5", "sunday": "6"}

def processAlarmDetails(googleString): # set an alarm for (today, tomorrow, friday) at five pm
    q = googleString.lower().split("set an alarm for ")[1]
    timeUnit = q.split(" ")[0]
    print(f"timeUnit: {timeUnit}")

    time = q.split(f"at ")[1].split(" ") # [5, p.m.]
    hour = int(time[0])
    if len(time) == 3:
        minute = time[1]
        isAM = time[2] == "a.m."
    else:
        minute = 0
        isAM = time[1] == "a.m."

    print(f"hour: {time}")
    print(f"isAM: {isAM}")

    now = datetime.now()
    if timeUnit == "today":
        alarmTime = datetime.today().replace(hour=hour, minute=int(minute), second=0, microsecond=0)
    elif timeUnit == "tomorrow":
        tomorrow = datetime.today() + timedelta(days=1)
        alarmTime = tomorrow.replace(hour=hour, minute=int(minute), second=0, microsecond=0)

    elif timeUnit in weekDays.keys():
        day = weekDays[timeUnit]
        today = now.weekday() 
        if day > today:
            daysToGo = day - today
        else:
            daysToGo = 7 - today + day

        alarmTime = datetime.today().replace(hour=hour, minute=int(minute), second=0, microsecond=0) + timedelta(days=daysToGo)
    else:
        print("Error")
        return

    description = q.split(" ")[2:]
    description = ' '.join(description)
    print(f"description: {description}")

    print(f"alarmTime: {alarmTime.isoformat()}")

    addToDB("alarm", "speech", "", alarmTime)
    return True

def processTimerDetails(googleString): # set a timer for (15 minutes, 2 hours)
    q = googleString.lower().split("set a timer for ")[1]
    restOfQ = q.split(" ")

    time = timeUnit = restOfQ[0]
    print(f"time: {time}")
    timeUnit = restOfQ[1]
    print(f"timeUnit: {timeUnit}")

    if timeUnit == "minutes" or timeUnit == "minute":
        alarmTime = datetime.now() + timedelta(minutes=int(time))
    elif timeUnit == "hours" or timeUnit == "hour":
        alarmTime = datetime.now() + timedelta(hours=int(time))

    print(f"alarmTime: {alarmTime.isoformat()}")

    addToDB("timer", "speech", "", alarmTime)
    return True


def getWeather(location):
    weather = weatherManager.weather_at_place(location).weather
    return weather.temperature("celsius")

def processGetWeather(googleString): # How is the weather. How is the weather in (location)
    # q = googleString.lower().split("set a timer for ")[1]

    location = "Monterrey,mx"
    result = getWeather(location)


    

rec = sr.Recognizer()
rec2 = sr.Recognizer()

while True:
    with sr.Microphone() as source:
        rec.adjust_for_ambient_noise(source, duration=1)
        rec2.adjust_for_ambient_noise(source, duration=1)
        print("Speak now")
        try:
           audio = rec.listen(source)
           string = rec.recognize_google(audio)
           print(string)
        except Exception as e:
           print(f"Error 1 {e}")
           string = ""
        if "hello" in string.lower():
            print("How can I help?")
            try:
                audio2 = rec2.listen(source)
                googleString = rec2.recognize_google(audio2)
                print(googleString)
                if "remind me in" in googleString.lower(): # remind me in twenty minutes to do something
                   success = processReminderDetails(googleString)

                if "set an alarm for " in googleString.lower(): # set an alarm for (tomorrow, friday) at five pm
                    success = processAlarmDetails(googleString)

                if "set a timer for " in googleString.lower(): # set a timer for (15 minutes, 2 hours)
                    success = processTimerDetails(googleString)

                if "How is the weather" in googleString.lower():
                    processGetWeather(googleString)

            except Exception as e:
               print(f"Exception Error: {e}")

        if "bye" in string.lower():
            print("Goodbye")
            break