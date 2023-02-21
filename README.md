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
Создание "superuser" после запуска контейнера подключиться к контейнеру "auth"
```
docker exec -it auth sh
env FLASK_APP=wsgi_app python -m flask create_superuser <superUser> <password>
```
Документация к API доступна по адресу http://localhost:8001/apidocs/
### Тесты
Для запуска тестов выполните команду
```
docker-compose -f tests/functional/docker-compose.tests.yml up --build
```
### Миграции
Для создания новой миграции выполните команду
```
cd auth/src
flask db migrate
```