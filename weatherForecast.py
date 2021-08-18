import pyowm
import credentials

API_KEY = credentials.openWeatherMapsAPIKey

openMap = pyowm.OWM(API_KEY)

weatherManager = openMap.weather_manager()

def getWeather(location="Monterrey,mx"):
    weather = weatherManager.weather_at_place(location).weather
    return weather.temperature("celsius")

print(getWeather())