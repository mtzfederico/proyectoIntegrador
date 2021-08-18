# https://gobiko.com/blog/token-based-authentication-http2-example-apns/
import json
import jwt # requiers pip3 install cryptography
import time
from hyper import HTTPConnection

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

    print(f"New token is: {newTokenUTF8}")
    print(f"generated at {newTokenGenTime}")
    return newTokenUTF8


def getToken():
    return "eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiIsImtpZCI6IkNSTjhINTk2SzQifQ.eyJpc3MiOiIzODVSQ05NWjVMIiwiaWF0IjoxNjI5MjQyNTgzLjc4MTEwNzJ9.pDig1tuJanuDwLMkElecGrJJz0ZpC0Uk_rBM6xe9BSjJM83vNFLn74iIDVwLXAguRwpjW-rAXpSSHuPo95K4cQ"
    # return generateToken()
    # return None
    # return "eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiIsImtpZCI6IkNSTjhINTk2SzQifQ.eyJpc3MiOiIzODVSQ05NWjVMIiwiaWF0IjoxNjI5MjQyNTgzLjc4MTEwNzJ9.pDig1tuJanuDwLMkElecGrJJz0ZpC0Uk_rBM6xe9BSjJM83vNFLn74iIDVwLXAguRwpjW-rAXpSSHuPo95K4cQ"
    # generated at 1629242221.2275255 

""""
def getToken(cursor):
    dbToken = None
    # "CREATE TABLE APNSJWT (JWT VARCHAR(255), creationEpoch BIGINT(255), app VARCHAR(255), id INT AUTO_INCREMENT PRIMARY KEY)"
    sqlCommand = "SELECT * FROM APNSJWT WHERE app = 'main'"
    cursor.execute(sqlCommand)

    myresult = cursor.fetchall()

    if cursor.rowcount == 0:
        print(color.red, f"[getToken] No token found in DB. Add one manually", color.end)
        return None

    tokenGenTime = myresult[0][1] #tokens are only valid for 60 minutes but they shouldn't be refreshed more than once every 20 minutes
    print(f"[getToken] tokenGenTime: {tokenGenTime}")

    dbToken = myresult[0][0]

    currentTime = time.time()

    timeDifference = currentTime - tokenGenTime

    if timeDifference >= 3300: # 3300 is 55 minutes in seconds
        print(color.red, f"JWT is expired by {color.purple}{timeDifference}{color.red} seconds", color.end)
        dbToken = generateToken(cursor)
    else:
        print(color.green, "JWT is still valid", color.end)

    return dbToken
"""

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

    for item in notifications:
        path = '/3/device/{0}'.format(item.deviceToken)
        payload = json.dumps(item.payload).encode('utf-8')

        # Send our request
        conn.request(
            'POST',
            path,
            payload,
            headers=item.headers
        )
        resp = conn.get_response()
        #print(resp.headers.items_())

        s = Switcher()

        result = resp.status # for default value in case it is a different value
        result = s.handleStatusCode(resp.status)
        print(result)

        """
        if resp.status == 200:
            print("status is 200 OK")
        else:
            print(f"status is: {resp.status}")
            """
        print(resp.read())

    conn.close()


def sendToAllUsers(payload, isProduction):
    token = getToken()

    if token == None:
        print("[sendToAllUsers] No Token")
        return

    tokens = ["b068987e2dea0f145bed17eac023cf1bd9b1e806e9dda93f82f731c1fa735023"]

    notificationsToSend = []

    for token in tokens:
        notification = Notification()

        notification.deviceToken = token
        notification.payload = payload

        notification.headers = {
            'apns-expiration': '0',
            'apns-priority': '10', # send 5 if it is not very important or if the payload contains content-available
            'apns-push-type': 'alert',
            'apns-topic': 'com.mtzfederico.proyectoIntegrador ',
            'authorization': f'bearer {token}'
        }
        notificationsToSend.append(notification)

    sendnotification(notificationsToSend, isProduction)

# https://developer.apple.com/documentation/usernotifications/setting_up_a_remote_notification_server/generating_a_remote_notification

if __name__ == '__main__':
    payload = {
        'aps': { 'alert': { 'title': 'This is a test' } },
        'type': 'demo',
    }

    sendToAllUsers(payload, False)

# notificationsToSend = [notificationToSend, notificationToSend2]
# sendnotification(notificationsToSend, True)
