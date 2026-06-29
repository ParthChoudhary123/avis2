import os
import requests

def get_weather_warnings(city):
    """
    Fetch weather for a city and return warning details if heavy rain, storm, or snow is predicted/occurring.
    """
    api_key = os.getenv('OPENWEATHER_API_KEY', 'mock_key_for_testing')
    
    if api_key == 'mock_key_for_testing' or not api_key:
        # Mock weather behavior based on city name for demo/testing
        city_lower = city.lower()
        if 'seattle' in city_lower or 'rain' in city_lower:
            return {
                'has_warning': True,
                'condition': 'Heavy Rain',
                'description': 'Heavy downpour (>12mm/h) expected. Logistics delays likely.',
                'source': 'Mock Weather Engine'
            }
        elif 'buffalo' in city_lower or 'snow' in city_lower:
            return {
                'has_warning': True,
                'condition': 'Heavy Snow',
                'description': 'Snow accumulation (>10cm) expected. Road blockages likely.',
                'source': 'Mock Weather Engine'
            }
        elif 'miami' in city_lower or 'storm' in city_lower:
            return {
                'has_warning': True,
                'condition': 'Thunderstorm',
                'description': 'Severe thunderstorm warning. Shipping suspended.',
                'source': 'Mock Weather Engine'
            }
        return {'has_warning': False, 'condition': 'Clear', 'description': 'Clear sky, good logistics flow.', 'source': 'Mock Weather Engine'}

    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            weather_main = data.get('weather', [{}])[0].get('main', '').lower()
            weather_desc = data.get('weather', [{}])[0].get('description', '').lower()
            
            has_warning = False
            condition = 'Clear'
            description = 'Normal weather conditions'
            
            if 'rain' in weather_main or 'drizzle' in weather_main:
                rain_vol = data.get('rain', {}).get('1h', 0)
                if rain_vol >= 10 or 'heavy' in weather_desc:
                    has_warning = True
                    condition = 'Heavy Rain'
                    description = f"Heavy rain ({rain_vol}mm/h) detected. High risk of shipping delays."
            elif 'snow' in weather_main:
                has_warning = True
                condition = 'Snow'
                description = f"Snowfall ({weather_desc}) detected. Road transit delays expected."
            elif 'thunderstorm' in weather_main or 'storm' in weather_main:
                has_warning = True
                condition = 'Thunderstorm'
                description = "Thunderstorm warnings active. Severe delay risks."

            return {
                'has_warning': has_warning,
                'condition': condition,
                'description': description,
                'source': 'OpenWeatherMap API'
            }
        else:
            return {
                'has_warning': False,
                'condition': 'Unknown',
                'description': f"Unable to fetch weather (API returned {response.status_code})",
                'source': 'OpenWeatherMap API Error Fallback'
            }
    except Exception as e:
        return {
            'has_warning': False,
            'condition': 'Offline',
            'description': f"Weather service offline: {str(e)}",
            'source': 'OpenWeatherMap Connection Error'
        }
