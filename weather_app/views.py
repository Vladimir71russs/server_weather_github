import requests
from django.conf import settings
from django.shortcuts import render
from datetime import datetime, timedelta


def extract_weather_data(data, city, date_time):
    # Проверяем, что данные корректны
    if 'main' in data and 'weather' in data:
        return {
            'city': city,
            'temperature': data['main']['temp'],
            'press': data['main']['pressure'],
            'wind': data['wind']['speed'],
            'description': data['weather'][0]['description'],
            'date_time': date_time
        }
    else:
        return None


def get_weather(request):
    city = request.GET.get('city', 'Moscow')
    forecast_type = request.GET.get('forecast_type', 'current')  # 'current', 'tomorrow', 'next_hours'
    api_key = settings.WEATHER_API_KEY
    weather_data = None

    if forecast_type == 'current':
        # Текущая погода
        url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=ru'
    elif forecast_type == 'tomorrow' or forecast_type == 'next_three_hours':
        # Прогноз погоды на завтра или на ближайшие 3 часа
        url = f'http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric&lang=ru'
    else:
        url = None

    if url:
        response = requests.get(url)
        data = response.json()

        # Обработка ошибки для неправильного города
        if 'message' in data and data['cod'] == '404':
            error_message = "Город не найден. Пожалуйста, введите существующий город."
            return render(request, 'weather_app/weather.html', {'error': error_message})

        # Данные для текущей погоды
        if forecast_type == 'current':
            weather_data = extract_weather_data(data, city, datetime.now())
            if weather_data is None:
                error_message = "Не удалось получить данные о погоде на сегодня."
                return render(request, 'weather_app/weather.html', {'error': error_message})

        # Прогноз на ближайшие 3 часа
        elif forecast_type == 'next_three_hours' and 'list' in data:
            now = datetime.now()
            target_time = now + timedelta(hours=3)
            target_timestamp = int(target_time.timestamp())

            # Ищем ближайший прогноз к целевому времени через 3 часа
            next_hours_data = None
            closest_diff = float('inf')  # Начальное значение для наименьшей разницы во времени

            for item in data['list']:
                forecast_timestamp = item['dt']
                time_diff = abs(forecast_timestamp - target_timestamp)

                if time_diff < closest_diff:
                    closest_diff = time_diff
                    next_hours_data = item

            # Если нашли данные для прогноза, обрабатываем их
            if next_hours_data:
                weather_data = extract_weather_data(next_hours_data, city, datetime.fromtimestamp(next_hours_data['dt']))
            else:
                error_message = "Не удалось получить данные о погоде на ближайшие 3 часа."
                return render(request, 'weather_app/weather.html', {'error': error_message})

        # Прогноз на завтра
        elif forecast_type == 'tomorrow' and 'list' in data:
            tomorrow_datetime = datetime.now().replace(hour=12, minute=0, second=0, microsecond=0) + timedelta(days=1)

            tomorrow_data = next(
                (
                    entry for entry in data['list']
                    if datetime.fromtimestamp(entry['dt']) == tomorrow_datetime
                ),
                None
            )

            if tomorrow_data:
                weather_data = extract_weather_data(tomorrow_data, city, tomorrow_datetime)
            else:
                error_message = "Не удалось получить данные о погоде на завтра."
                return render(request, 'weather_app/weather.html', {'error': error_message})

        return render(request, 'weather_app/weather.html', {'weather': weather_data})

    # Если URL не определен или возникла другая ошибка
    error_message = "Не удалось получить данные о погоде."
    return render(request, 'weather_app/weather.html', {'error': error_message})
