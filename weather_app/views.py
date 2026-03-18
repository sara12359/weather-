from django.shortcuts import render, redirect
import requests
from django.conf import settings
from .models import FavoriteCity, WeatherRecord
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Avg
from django.db.models.functions import TruncDate

def get_weather_emoji(main_weather):
    if main_weather == 'Clear':
        return '☀️'
    elif main_weather in ['Rain', 'Drizzle', 'Thunderstorm']:
        return '🌧'
    elif main_weather == 'Clouds':
        return '☁️'
    elif main_weather == 'Snow':
        return '❄️'
    return '☁️'

def weather_view(request):
    weather_data = None
    forecast_data = []
    error_message = None
    city = None

    if request.method == 'POST' or request.GET.get('city'):
        city = request.POST.get('city') or request.GET.get('city')
        lat = request.POST.get('lat')
        lon = request.POST.get('lon')
        
        if city or (lat and lon):
            api_key = settings.OPENWEATHER_API_KEY
            if lat and lon and not city:
                url_current = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
                url_forecast = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric"
            else:
                url_current = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
                url_forecast = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"
            
            try:
                response = requests.get(url_current)
                data = response.json()
                
                if response.status_code == 200:
                    city_name = data['name']
                    main_weather = data['weather'][0]['main']
                    emoji = get_weather_emoji(main_weather)
                    
                    # Convert sunrise and sunset
                    sunrise = datetime.fromtimestamp(data['sys']['sunrise']).strftime('%H:%M')
                    sunset = datetime.fromtimestamp(data['sys']['sunset']).strftime('%H:%M')
                    wind_speed = data['wind']['speed']
                    temp = data['main']['temp']
                    humidity = data['main']['humidity']
                    desc = data['weather'][0]['description']
                    
                    weather_data = {
                        'city': city_name,
                        'temperature': temp,
                        'feels_like': data['main']['feels_like'],
                        'humidity': humidity,
                        'pressure': data['main']['pressure'],
                        'visibility': data.get('visibility', 0) / 1000, # km
                        'description': desc.capitalize(),
                        'icon': data['weather'][0]['icon'],
                        'emoji': emoji,
                        'wind_speed': wind_speed,
                        'sunrise': sunrise,
                        'sunset': sunset,
                        'lat': data['coord']['lat'],
                        'lon': data['coord']['lon'],
                    }
                    
                    # Save to database
                    WeatherRecord.objects.create(
                        city=city_name,
                        temperature=temp,
                        humidity=humidity,
                        wind_speed=wind_speed,
                        description=desc,
                        lat=data['coord']['lat'],
                        lon=data['coord']['lon']
                    )
                    
                    # Fetch Forecast
                    resp_forecast = requests.get(url_forecast)
                    if resp_forecast.status_code == 200:
                        f_data = resp_forecast.json()
                        daily_forecasts = []
                        seen_days = set()
                        for item in f_data['list']:
                            dt = datetime.fromtimestamp(item['dt'])
                            day = dt.strftime('%A')
                            # Default approx 12-15 hr block if possible, or just pick first encountered
                            if day not in seen_days and (dt.hour >= 11 and dt.hour <= 15):
                                seen_days.add(day)
                                daily_forecasts.append({
                                    'day': day,
                                    'temp': round(item['main']['temp'], 1),
                                    'emoji': get_weather_emoji(item['weather'][0]['main'])
                                })
                            if len(daily_forecasts) >= 5:
                                break
                        
                        if len(daily_forecasts) < 5:
                            daily_forecasts = []
                            seen_days = set()
                            for item in f_data['list']:
                                dt = datetime.fromtimestamp(item['dt'])
                                day = dt.strftime('%A')
                                if day not in seen_days:
                                    seen_days.add(day)
                                    daily_forecasts.append({
                                        'day': day,
                                        'temp': round(item['main']['temp'], 1),
                                        'emoji': get_weather_emoji(item['weather'][0]['main'])
                                    })
                                if len(daily_forecasts) >= 5:
                                    break
                                    
                        forecast_data = daily_forecasts
                        
                        # Extract hourly forecast for charts (first 8 items)
                        chart_labels = []
                        chart_data = []
                        for item in f_data['list'][:8]:
                            chart_labels.append(datetime.fromtimestamp(item['dt']).strftime('%H:%M'))
                            chart_data.append(item['main']['temp'])
                        
                        weather_data['chart_labels'] = chart_labels
                        weather_data['chart_data'] = chart_data
                        
                else:
                    error_message = f"City '{city}' not found." if city else "Location not found."
            except Exception as e:
                error_message = f"An error occurred: {str(e)}"

    favorites = FavoriteCity.objects.all()
    favorite_names = [f.name for f in favorites]
    is_favorite = False
    if weather_data and weather_data['city'] in favorite_names:
        is_favorite = True

    return render(request, 'weather_app/index.html', {
        'weather_data': weather_data,
        'forecast_data': forecast_data,
        'error_message': error_message,
        'city': city,
        'favorites': favorites,
        'is_favorite': is_favorite
    })

def toggle_favorite(request):
    if request.method == 'POST':
        city_name = request.POST.get('city')
        if city_name:
            fav, created = FavoriteCity.objects.get_or_create(name=city_name)
            if not created:
                fav.delete()
    return redirect('weather_view')

def dashboard_view(request):
    thirty_days_ago = timezone.now() - timedelta(days=30)
    records = WeatherRecord.objects.filter(timestamp__gte=thirty_days_ago)
    
    top_cities = records.values('city').annotate(avg_temp=Avg('temperature')).order_by('-avg_temp')[:10]
    
    selected_city = request.GET.get('city')
    if not selected_city and records.exists():
        selected_city = records.first().city
        
    chart_labels = []
    chart_data = []
    
    if selected_city:
        city_records = records.filter(city=selected_city).annotate(
            date=TruncDate('timestamp')
        ).values('date').annotate(
            avg_temp=Avg('temperature')
        ).order_by('date')
        
        for r in city_records:
            chart_labels.append(r['date'].strftime('%b %d'))
            chart_data.append(round(r['avg_temp'], 1))
            
    all_cities = list(WeatherRecord.objects.values_list('city', flat=True).distinct())
            
    # Comparison Logic
    compare_city = request.GET.get('compare_city')
    compare_chart_data = []
    if compare_city:
        compare_records = records.filter(city=compare_city).annotate(
            date=TruncDate('timestamp')
        ).values('date').annotate(
            avg_temp=Avg('temperature')
        ).order_by('date')
        
        # Syncing dates is tricky if they have different record days
        # For simplicity, we'll just send the data and let the frontend tooltips handle it, 
        # or just assume they overlap for now labels are based on the main city.
        compare_chart_data = [round(r['avg_temp'], 1) for r in compare_records]

    # Map Coordinates
    selected_lat = None
    selected_lon = None
    if selected_city:
        last_record = WeatherRecord.objects.filter(city=selected_city).exclude(lat__isnull=True).order_by('-timestamp').first()
        if last_record:
            selected_lat = last_record.lat
            selected_lon = last_record.lon

    context = {
        'top_cities': top_cities,
        'selected_city': selected_city,
        'selected_lat': selected_lat,
        'selected_lon': selected_lon,
        'compare_city': compare_city,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'compare_chart_data': compare_chart_data,
        'all_cities': all_cities,
    }
    return render(request, 'weather_app/dashboard.html', context)
