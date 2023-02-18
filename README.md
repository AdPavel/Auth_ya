# Сервис AUTH
### Как установить локально
1. Установите зависимости
```
pip install - r auth/requirements.txt
```
2. Поднимите сервис
```
cd auth/src
gunicorn --bind 0.0.0.0:8000 wsgi_app:app 
```
### С помощью docker
```
docker-compose up -d --build
```
Документация к API доступна по адресу http://127.0.0.1:8001/apidocs/