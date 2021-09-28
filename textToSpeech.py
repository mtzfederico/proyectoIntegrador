"""
    iOSNotifications.py

    This file contains the Text to Speach (TTS) related functions.
    It is imported in some files.
    It requires an internet connection and some speakers.
"""

from gtts import gTTS
import os
from playsound import playsound
import platform

def say(text):
    try:
        if text is None or text == "":
            playsound('doorbell-2.wav')
            return

        language = 'en'

        # Passing the text and language to the engine, 
        # here we have marked slow=False. Which tells 
        # the module that the converted audio should 
        # have a high speed
        myobj = gTTS(text=text, lang=language, slow=False)

        # Saving the converted audio in a mp3 file named
        # welcome 
        myobj.save("message.mp3")

        print("Playing TTS")
        # Playing the converted file
        system = platform.system() # https://stackoverflow.com/questions/1854/python-what-os-am-i-running-on
        if system == "Darwin":
            playsound('message.mp3')
        else:
            os.system("omxplayer message.mp3")

        os.remove("message.mp3")
        print("Removed TTS file")
        return
    except Exception as e:
        print(f"TTS Message: {text}")
        print(f"[Say] Error: {e}")

if __name__ == "__main__":
    say("Hello World")