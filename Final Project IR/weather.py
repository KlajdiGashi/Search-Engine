# weather.py

import requests

def get_weather(city):
    api_key = '7fb72c65b519874cf3614633b4ad10a8'
    base_url = 'http://api.openweathermap.org/data/2.5/weather'
    params = {'q': city, 'appid': api_key, 'units': 'metric'}
    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        return None
