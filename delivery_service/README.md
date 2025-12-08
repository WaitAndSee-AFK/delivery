Проект службы доставки на Django с Docker и PostgreSQL.

## 🚀 Быстрый старт

### Требования
- Docker
- Docker Compose

### Запуск проекта

1. Клонируйте репозиторий:
git clone https://github.com/ваш-username/delivery-service.git
cd delivery-service/delivery_service

2. Запустите Docker Compose:
docker-compose up -d --build

3. Примените миграции (если не применились автоматически):
docker-compose exec web python manage.py migrate

4. Создайте суперпользователя:
docker-compose exec web python manage.py createsuperuser

5. Откройте в браузере:
Сайт: http://localhost:8000
Админка: http://localhost:8000/admin