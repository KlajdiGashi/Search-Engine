from flask import render_template, request
from . import app
import requests

def get_weather(city):
    api_key = '7fb72c65b519874cf3614633b4ad10a8'  # Replace with your actual API key
    base_url = f'http://api.openweathermap.org/data/2.5/weather'
    params = {'q': city, 'appid': api_key, 'units': 'metric'}
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None

@app.route('/weather')
def weather():
    city = request.args.get('city', 'London')  # Default to London if city parameter not provided
    weather_data = get_weather(city)
    if weather_data:
        temperature = weather_data['main']['temp']
        description = weather_data['weather'][0]['description']
        humidity = weather_data['main']['humidity']
        return render_template('weather.html', temperature=temperature, description=description, humidity=humidity)
    else:
        return render_template('weather.html', error=True)

import sys
print(sys.path)
