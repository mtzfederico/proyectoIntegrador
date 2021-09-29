# Proyecto Integrador

This is a voice assistant program with a helper iOS app.
This program let's you control things with voice and set alarms.

This program consists of three parts. The voice assistant program, the web server, and the alarm notifier program.

The voice assistant program (voiceRecognition.py), runs constantly and when it is called it runs the specified action.

The Web Server (webServer.py), runs constantly and it handles requests from the iOS app.

The alarm notifier program (checkAlarms.py), runs constantly and checks if an an alarm's alarmTime has already passed and notifies the user via iOS notifications or TTS.


# Dependencies:

## Voice Assistant Program:
The `speech_recognition` library with Google's STT
The `textToSpeech`, `mqttFunctions` and `weatherForecast` files

## The Web Server:
`Flask`
`sqlite3`
The `mqttFunctions` and `weatherForecast` files

## The alarm notifier program:
`sqlite3`
The `textToSpeech`, `iOSNotifications` and `credentials` files


# Installation:
1. Clone this repository by running:

    $ git clone https://github.com/mtzfederico/proyectoIntegrador

2. install the required python libraries by running:

    $ pip install -r requirements.txt

3. Create the credentials file so that it has your API and APNS keys. Take a look at credentials_Template.py


2. Run the setup script:

    $ python3 setup.py