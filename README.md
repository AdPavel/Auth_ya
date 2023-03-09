# Сервис AUTH
### Как установить локально
1. Установите зависимости
```
pip install - r auth/requirements.txt
```
2. Примените миграции
```
cd auth/src
flask db upgrade
```
3. Поднимите сервис
```
cd auth/src
gunicorn --bind 0.0.0.0:8000 wsgi_app:app 
```
### С помощью docker
```
docker-compose up -d --build
```
### Обязательно создание "superuser" после запуска контейнера подключиться к контейнеру "auth"
```
docker exec -it auth sh
flask create_superuser <superUser> <password>
```
Документация к API доступна по адресу http://localhost/apidocs/
### Тесты
Для запуска тестов выполните команду
```
docker-compose -f tests/functional/docker-compose.tests.yml up --build
```
### Миграции
Для создания новой миграции выполните команду

 Локально
```
cd auth/src
flask db migrate
```
 Для контейнера
```
docker exec -it auth sh
flask db migrate
```

### Настройка Rate Limit
 Для того что бы снять ограничение количества запросов к серверу (Rate limit
 ) нужно установить максимальное числа в .env для RATE_LIMIT_REQUEST (например 100 000
 ) и минимальное для RATE_LIMIT_TIME (например 1, не должно быть 0)  

### Интеграция с fastapi
Функции для интеграции реализованы в https://github.com/AdPavel/fastapi_yapr

