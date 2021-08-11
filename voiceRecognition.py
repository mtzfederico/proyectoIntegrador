import speech_recognition as sr
# from word2number import w2n
from datetime import datetime
from datetime import timedelta
# from datetime import date

def addToDB():
    pass

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

    addToDB()
    return alarmTime, description

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

    print(f"alarmTime: {alarmTime}")

    addToDB()
    return alarmTime, description


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
                   alarmTime, description = processReminderDetails(googleString)
                   print("")

                if "set an alarm for " in googleString.lower(): # set an alarm for (tomorrow, friday) at five pm
                    alarmTime, description = processAlarmDetails(googleString)

            except Exception as e:
               print(f"Error {e}")

        if "bye" in string.lower():
            print("Goodbye")
            break