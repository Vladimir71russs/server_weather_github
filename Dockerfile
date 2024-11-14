# Используем официальный образ Python
FROM python:3.12-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальные файлы
COPY . .

# Добавляем команду для выполнения миграций перед запуском сервера
CMD ["sh", "-c", "python manage.py migrate && gunicorn weat.wsgi:application --bind 0.0.0.0:8000"]
