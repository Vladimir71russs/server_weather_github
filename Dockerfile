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



# Указываем команду по умолчанию
#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
CMD ["gunicorn", "weather.wsgi:application", "--bind", "0.0.0.0:8000"]