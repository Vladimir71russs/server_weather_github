from datetime import timedelta
from django.conf import settings
from django.core.mail import send_mail

import requests

from .models import NotificationSetting
from django.utils import timezone
from celery import shared_task


@shared_task
def send_weather_notifications():
    notifications = NotificationSetting.objects.all()

    for notification in notifications:
        # Проверка частоты уведомлений
        last_sent = notification.last_sent
        now = timezone.now()

        if (notification.frequency == 'hourly' and last_sent and (now - last_sent) < timedelta(hours=1)) or \
           (notification.frequency == 'daily_9am' and last_sent and (now - last_sent) < timedelta(days=1)):
            continue  # Пропускаем, если уведомление уже было отправлено в заданный интервал

        # Получение данных о погоде
        api_key = settings.WEATHER_API_KEY
        city = notification.city.capitalize()  # Используем город с первой заглавной буквы
        response = requests.get(f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=ru')

        if response.status_code == 200:
            weather_data = response.json()
            weather_description = weather_data['weather'][0]['description']
            temperature = weather_data['main']['temp']
            press = weather_data['main']['pressure']
            wind = weather_data['wind']['speed']

            # Перевод давления в мм рт. ст.
            pressure_mmhg = int(press * 0.75006)

            # Текущая дата и время по МСК
            moscow_time = now.astimezone(timezone.get_default_timezone()).strftime("%d.%m.%Y %H:%M")

            # Текст сообщения
            email_subject = f'Прогноз погоды от team.Dorofeev'
            email_message = (
                f"Город: {city}\n"
                f"Время прогноза: на {moscow_time} (по МСК)\n"
                f"Описание: {weather_description}\n"
                f"Температура: {temperature}°C\n"
                f"Скорость ветра: {wind} м/с\n"
                f"Давление: {pressure_mmhg} мм рт. ст.\n\n"
                f"С уважением,\nВаша команда."
            )

            # Отправка email
            send_mail(
                email_subject,
                email_message,
                settings.EMAIL_HOST_USER,
                [notification.user.email],
                fail_silently=False,
            )

            # Обновляем время последней отправки
            notification.last_sent = now
            notification.save()
