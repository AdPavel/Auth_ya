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
docker-compose -d --build up
```
