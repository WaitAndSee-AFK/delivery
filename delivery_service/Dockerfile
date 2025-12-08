FROM python:3.11-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Собираем статику (если используется)
# RUN python manage.py collectstatic --noinput

# Открываем порт
EXPOSE 8000

# Команда запуска (будет переопределена в docker-compose)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "delivery_service.wsgi:application"]