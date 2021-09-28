"""
    weatherForecast.py

    This is file contains the weather API functions.
    It requires an API key from Open Weather Maps to be stored in the credentials.py file.
    It is imported in some files.
"""

import pyowm
import credentials

API_KEY = credentials.openWeatherMapsAPIKey

openMap = pyowm.OWM(API_KEY)

weatherManager = openMap.weather_manager()

# Fetches the current weather at the specified location. Returns temperature in celsius
def getTemp(location="Monterrey,mx"):
    weather = weatherManager.weather_at_place(location).weather
    return weather.temperature("celsius")["temp"]

if __name__ == "__main__":
    print(getTemp())