import json
import jwt # requiers pip3 install cryptography
import time
from hyper import HTTPConnection
import sqlite3
from sqlite3 import Error

# https://gobiko.com/blog/token-based-authentication-http2-example-apns/
# https://developer.apple.com/documentation/usernotifications/setting_up_a_remote_notification_server/generating_a_remote_notification
# https://developer.apple.com/documentation/usernotifications/setting_up_a_remote_notification_server/sending_notification_requests_to_apns
# https://developer.apple.com/documentation/usernotifications/setting_up_a_remote_notification_server/handling_notification_responses_from_apns

class color:
    purple = '\033[95m'
    blue = '\033[94m'
    green = '\033[92m'
    red = '\033[91m'
    end = '\033[0m'

ALGORITHM = 'ES256'
APNS_KEY_ID = 'CRN8H596K4' # actual key
APNS_AUTH_KEY = 'AuthKey_CRN8H596K4.p8' # this is the path, file is in the same folder
TEAM_ID = '385RCNMZ5L' # actual team id

def connectToDB():
    try:
        db_file = "APNS.db"
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(f"[connectToDB] Error: {e}")
    finally:
        return conn

def createTable(conn):
    sqlTable = """CREATE TABLE IF NOT EXISTS APNSProviderToken (
                                        JWT text NOT NULL,
                                        creationEpoch text NOT NULL,
                                        app text NOT NULL,
                                        id integer PRIMARY KEY
                                    );"""

    try:
        c = conn.cursor()
        c.execute(sqlTable)
    except Error as e:
        print(e)

conn = connectToDB()
createTable(conn)

# https://jaxenter.com/implement-switch-case-statement-python-138315.html
class Switcher(object):
    def handleStatusCode(self,i):
        method_name='number_'+str(i)
        method=getattr(self,method_name,lambda :'Invalid')
        return method()
    def number_200(self):
        return 'success'
    def number_400(self):
        return 'bad request'
    def number_403(self):
        return 'provider token error'
    def number_405(self):
        return 'bad :method, use POST'
    def number_410(self):
        return 'bad device token for the topic (aka app)'
    def number_413(self):
        return 'payload too big'
    def number_429(self):
        return 'too many requests for device token'
    def number_500(self):
        return 'server error'
    def number_503(self):
        return 'server is shutting down and unavailable'


def generateToken():
    f = open(APNS_AUTH_KEY)
    secret = f.read()

    newTokenGenTime = time.time()

    newToken = jwt.encode(
        {
            'iss': TEAM_ID,
            'iat': newTokenGenTime
        },
        secret,
        algorithm= ALGORITHM,
        headers={
            'alg': ALGORITHM,
            'kid': APNS_KEY_ID,
        }
    )

    newTokenUTF8 = newToken.decode('utf-8')

    if conn == None:
        connectToDB()

    try:
        command = "UPDATE APNSProviderToken SET JWT = ?, creationEpoch = ? WHERE app = 'main'"
        values = (newTokenUTF8, newTokenGenTime)
        cur = conn.cursor()
        cur.execute(command, values)
        conn.commit()

    except Exception as e:
        print(f"{color.red}[generateToken] Error:{color.end} {e}")
    finally:
        print(f"{color.green}Saved Provider Token{color.end}")


    print(f"New token is: {newTokenUTF8}")
    print(f"generated at {newTokenGenTime}")
    return newTokenUTF8


def getToken():
    if conn == None:
        connectToDB()

    dbToken = None
    cur = conn.cursor()
    command = "SELECT * FROM APNSProviderToken WHERE app = 'main'"
    cur.execute(command)

    myresult = cur.fetchall()

    if len(myresult) <= 0:
        print(color.red, f"[getToken] No token found in DB. Generating one", color.end)
        command = "INSERT INTO APNSProviderToken(JWT, creationEpoch, app) VALUES(?, ?, ?)"
        values = ("", "0", "main")
        cur.execute(command, values)
        conn.commit()
        newToken = generateToken()

        return newToken

    tokenGenTime = myresult[0][1] #tokens are only valid for 60 minutes but they shouldn't be refreshed more than once every 20 minutes
    print(f"[getToken] tokenGenTime: {tokenGenTime}")

    dbToken = myresult[0][0]

    currentTime = time.time()

    timeDifference = currentTime - float(tokenGenTime)

    if timeDifference >= 3300: # 3300 is 55 minutes in seconds
        print(color.red, f"JWT is expired by {color.purple}{timeDifference}{color.red} seconds", color.end)
        dbToken = generateToken()
    else:
        print(color.green, "JWT is still valid", color.end)

    return dbToken


class Notification:
    deviceToken = ''
    headers = {}
    payload = {}


def sendnotification(notifications, isProduction=False):
    # Open a connection the APNS server
    serverURL = 'api.sandbox.push.apple.com:443'

    if isProduction:
        serverURL = 'api.push.apple.com:443'

    conn = HTTPConnection(serverURL) # production url is api.push.apple.com  optional port 2197  development is api.sandbox.push.apple.com

    for notification in notifications:
        path = '/3/device/{0}'.format(notification.deviceToken)
        payload = json.dumps(notification.payload).encode('utf-8')

        # Send our request
        conn.request(
            'POST',
            path,
            payload,
            headers=notification.headers
        )
        resp = conn.get_response()
        #print(resp.headers.items_())

        s = Switcher()

        result = resp.status # for default value in case it is a different value
        result = s.handleStatusCode(resp.status)
        print(result)

        print(resp.read())

    conn.close()


def notifyAllUsers(payload, deviceTokens, isProduction=False):
    providerToken = getToken()

    if providerToken == None:
        print("[notifyAllUsers] No providerToken")
        return

    notificationsToSend = []

    for deviceToken in deviceTokens:
        notification = Notification()

        notification.deviceToken = deviceToken
        notification.payload = payload

        notification.headers = {
            'apns-expiration': '0',
            'apns-priority': '10', # send 5 if it is not very important or if the payload contains content-available
            'apns-push-type': 'alert',
            'apns-topic': 'com.mtzfederico.proyectoIntegrador',
            'authorization': f'bearer {providerToken}'
        }
        notificationsToSend.append(notification)

    sendnotification(notificationsToSend, isProduction)

if __name__ == '__main__':
    payload = {
        'aps': { 'alert': { 'title': 'Test', 'body': 'This is a test notification' } },
        'type': 'test',
    }

    deviceTokens = ["b068987e2dea0f145bed17eac023cf1bd9b1e806e9dda93f82f731c1fa735023"]

    notifyAllUsers(payload, deviceTokens, False)