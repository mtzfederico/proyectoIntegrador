import speech_recognition as sr
# from word2number import w2n
from datetime import datetime
from datetime import timedelta
import sqlite3
from sqlite3 import Error
import pyowm
import credentials
import textToSpeech
import mqttFunctions
import time

# Colors used for printing
class color:
    purple = '\033[95m'
    blue = '\033[94m'
    green = '\033[92m'
    red = '\033[91m'
    end = '\033[0m'

openMap = pyowm.OWM(credentials.openWeatherMapsAPIKey)
weatherManager = openMap.weather_manager()

def connectToDB():
    try:
        db_file = "alarms.db"
        conn = sqlite3.connect(db_file)
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
        values = (type, notificationType, optionalMessage, creationDate, alarmDate)
        cur = conn.cursor()
        cur.execute(command, values)
        conn.commit()

    except Exception as e:
        print(f"{color.red}[addToDB] Error:{color.end} {e}")
        return False
    finally:
        print("Saved")
        return True
    
# Proccesses the set a reminder command
def processReminderDetails(googleString): # remind me in twenty minutes to do something
    q = googleString.lower().split("remind me in ")[1]
    timeUnit = q.split(" ")[1]

    time = q.split(f" {timeUnit}")[0]
    print(f"time: {time}")

    # Gets the reminder's timeUnit
    now = datetime.now()
    if timeUnit == "minutes" or timeUnit == "minute":
        alarmTime = now + timedelta(minutes=int(time))
    elif timeUnit == "seconds":
        alarmTime = now + timedelta(seconds=int(time))
    elif timeUnit == "hours" or timeUnit == "hour":
        alarmTime = now + timedelta(hours=int(time))
    elif timeUnit == "days" or timeUnit == "day":
        alarmTime = now + timedelta(days=int(time))

    print(f"timeUnit: {timeUnit}")

    description = q.split(" ")[2:]
    message = ' '.join(description)
    print(f"message: {message}")

    print(f"alarmTime: {alarmTime}")

    success = addToDB("reminder", "notification", message, alarmTime)

    if success == False:
        textToSpeech.say("Error saving Reminder")


weekDays = {"monday": "0", "tuesday": "1", "wednesday": "2", "thursday": "3", "friday": "4", "saturday": "5", "sunday": "6"}

# Proccesses the set an alarm command
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

    # Gets the alarm's time and date fron the speech
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
        print(color.red, "[processAlarmDetails] Error", color.end)
        return

    description = q.split(" ")[2:]
    description = ' '.join(description)
    print(f"description: {description}")

    print(f"alarmTime: {alarmTime.isoformat()}")

    success = addToDB("alarm", "notification", "", alarmTime)
    if success == False:
        textToSpeech.say("Error saving alarm")

# Proccesses the set a timer command
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

    print(f"{color.purple}alarmTime: {alarmTime.isoformat()}", color.end())

    success = addToDB("timer", "notification", "This is a test", alarmTime)
    
    if success == False:
        textToSpeech.say("Error saving timer")

# Fetches the current weather at the specified location. Returns temperature in celsius
def getWeather(location):
    weather = weatherManager.weather_at_place(location).weather
    return weather.temperature("celsius")

# Proccesses the get weather command
def processGetWeather(googleString): # How is the weather. How is the weather in (location)

    location = "Monterrey,mx"
    result = getWeather(location)

    textToSpeech.say(f"The teperature is {result} degrees celsius")

def gotRoomTemperature():
    textToSpeech.say(f"The room teperature is {mqttFunctions.latestTemp} degrees celsius")

# Proccesses the get room temperature command
def processGetRoomTemperature(): # What's the room temperature
    mqttFunctions.tempCallBack = gotRoomTemperature
    mqttFunctions.askForTemp()

    
# Voice recognizer instances used.
# There has to be two because they fail when used twice in a row
rec = sr.Recognizer()
rec2 = sr.Recognizer()

# Loop starts
while True:
    # starts the microphone
    with sr.Microphone() as source:
        rec.adjust_for_ambient_noise(source, duration=1)
        rec2.adjust_for_ambient_noise(source, duration=1)
        print(color.purple,"Speak now", color.end)
        try:
            # Starts listening
           audio = rec.listen(source)
           # The audio is sent to google for processing
           string = rec.recognize_google(audio)
           print(string)
        except Exception as e:
           print(f"{color.red}Error 1:{color.end} {e}")
           string = ""
        # Looks for the trigger word
        if "hello" in string.lower():
            print(color.green, "How can I help?", color.end) # You can say the command after seeing this message
            try:
                # Starts listening for the command using the second recognizer instance
                audio2 = rec2.listen(source)
                googleString = rec2.recognize_google(audio2)
                print(googleString)
                # Looks for the command and runs it's function
                if "remind me in" in googleString.lower(): # remind me in twenty minutes to do something
                   processReminderDetails(googleString)

                if "set an alarm for " in googleString.lower(): # set an alarm for (tomorrow, friday) at five pm
                    processAlarmDetails(googleString)

                if "set a timer for " in googleString.lower(): # set a timer for (15 minutes, 2 hours)
                    processTimerDetails(googleString)

                if "How is the weather" in googleString.lower():
                    processGetWeather(googleString)
                
                if "what's the room temperature" in googleString.lower(): # What's the room temperature
                    processGetRoomTemperature()

            # Handles errors in the commands
            except Exception as e:
               print(f"{color.red}Exception Error:{color.end} {e}")

        # If the user says bye the program ends
        if "bye" in string.lower():
            print(color.purple,"Goodbye", color.end)
            break