# WARNING: This file contains private keys
"""
    credentials.py

    This file contains the credentials used for API's.
    It is imported in some files.
"""

openWeatherMapsAPIKey = "<API_KEY_GOES_HERE>"

# iOS notification
APNS_KEY_ID = '<APNS_KEY_ID_GOES_HERE>' # You get this when you generate a JWT APNS key
APNS_AUTH_KEY = '<APNS_KEY_FILE_PATH_GOES_HERE>' # The JWT APNS key file (ends in .p8)
TEAM_ID = '<YOUR_APPLE_ACCOUNT_TEAM_ID_GOES_HERE>'

APNS_TOPIC = "com.apple.sampleAPP" # the iOS app's bundle id

MQTTServerIP = "10.0.0.53"
MQTTServerPort = 1883