import os
import platform
import sys

class color:
    purple = '\033[95m'
    blue = '\033[94m'
    green = '\033[92m'
    red = '\033[91m'
    end = '\033[0m'

system = platform.system() # https://stackoverflow.com/questions/1854/python-what-os-am-i-running-on
if system != "Linux":
    sys.exit(f"{color.red}Error:{color.end} The program can only run in Linux")



print("Installing python requirements")
os.system("pip install -r requirements.txt")

currentDIR = os.getcwd()

# https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-20-04
# https://github.com/torfsen/python-systemd-tutorial

serverServiceFileContents = f"""
[Unit]
Description=Proyecto Integredor-webServer
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory={currentDIR}
Environment="PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin"
ExecStart=gunicorn --bind 0.0.0.0:9080 wsgi:app
Restart=on-failure

[Install]
WantedBy=multi-user.target
"""

# gunicorn --workers 3 --bind unix:myproject.sock -m 007 wsgi:app

# print(serverServiceFileContents)

try:
    f = open("proyectoIntegrador-webServer.service", "x")

    f.write(serverServiceFileContents)
    f.close()
except Exception as error:
    print(f"{color.red}Write service file error:{color.end} {error}")
finally:
    print(color.green, "Saved service file", color.end)
    os.system(f"systemctl link {currentDIR}/proyectoIntegrador-webServer.service")


# make another service file for checkAlarms.py


# figure out how to leave voiceRecognition.py running