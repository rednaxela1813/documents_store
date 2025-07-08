# Используем официальный Python-образ
FROM python:3.12-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    libpq-dev gcc curl && \
    rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем requirements.txt и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/app:/app/backend




# Копируем весь код проекта
COPY . .

# Открываем порт для dev-сервера
EXPOSE 8000

# Используем manage.py runserver для dev
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
