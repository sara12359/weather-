from django.shortcuts import render
import requests
from django.conf import settings

def weather_view(request):
    weather_data = None
    error_message = None
    city = None

    if request.method == 'POST':
        city = request.POST.get('city')
        if city:
            api_key = settings.OPENWEATHER_API_KEY
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
            
            try:
                response = requests.get(url)
                data = response.json()
                
                if response.status_code == 200:
                    main_weather = data['weather'][0]['main']
                    emoji = '☁️'
                    if main_weather == 'Clear':
                        emoji = '☀️'
                    elif main_weather in ['Rain', 'Drizzle', 'Thunderstorm']:
                        emoji = '🌧'
                    elif main_weather == 'Clouds':
                        emoji = '☁️'
                    
                    weather_data = {
                        'city': data['name'],
                        'temperature': data['main']['temp'],
                        'humidity': data['main']['humidity'],
                        'description': data['weather'][0]['description'],
                        'icon': data['weather'][0]['icon'],
                        'emoji': emoji,
                    }
                else:
                    error_message = f"City '{city}' not found."
            except Exception as e:
                error_message = "An error occurred while fetching weather data."

    return render(request, 'weather_app/index.html', {
        'weather_data': weather_data,
        'error_message': error_message,
        'city': city
    })
