# PVZ Automation — Django приложение
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода приложения
COPY . .

# Порт Django
EXPOSE 8000

# Миграции + запуск сервера
CMD python manage.py migrate --noinput && \
    python manage.py runserver 0.0.0.0:8000
