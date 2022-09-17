[![example workflow](https://github.com/caveinfix/foodgram-project-react/actions/workflows/main.yml/badge.svg)](http://fgram.ddns.net/recipes) 

# Проект «Продуктовый помощник» 
«Продуктовый помощник»: сайт, на котором пользователи будут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Сервис «Список покупок» позволит пользователям создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Превью

![App Screenshot](https://i2.paste.pics/a255c4101805a63342e983333a9fe415.png)

## Технологии
[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/) [![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/) [![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat-square&logo=Django%20REST%20Framework)](https://www.django-rest-framework.org/) [![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat-square&logo=PostgreSQL)](https://www.postgresql.org/) [![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat-square&logo=NGINX)](https://nginx.org/ru/) [![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat-square&logo=gunicorn)](https://gunicorn.org/) [![docker](https://img.shields.io/badge/-Docker-464646?style=flat-square&logo=docker)](https://www.docker.com/) [![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat-square&logo=GitHub%20actions)](https://github.com/features/actions) [![Yandex.Cloud](https://img.shields.io/badge/-Yandex.Cloud-464646?style=flat-square&logo=Yandex.Cloud)](https://cloud.yandex.ru/)
## Релиз
Сайт доступен по ссылке: [fgram.ddns.net](http://fgram.ddns.net/recipes)
Документация API: [fgram.ddns.net/api/docs](http://fgram.ddns.net/api/docs/)

## Подготовка к запуску на удаленном сервере
Сделайте форк и клонируйте репозиторий на локальную машину:
```bash
  git clone git@github.com:caveinfix/foodgram-project-react.git
```
Отредактируйте файл infra/nginx.conf, указав IP Вашего сервера:
```bash
server_name <IP Вашего сервера>;
```
Далее скопируйте файлы, находящиеся в папке infra на Ваш сервер, в домашнюю директорию:
```bash
scp docker-compose.yml <username>@<host>:/home/<username>/docker-compose.yml
scp nginx.conf <username>@<host>:/home/<username>/nginx.conf
```
Пример:
```bash
scp docker-compose.yaml caveinfix@158.160.7.100:/home/caveinfix/
```
### На удаленном сервере

В домашней директории создайте файл .env, куда были скопированы файлы docker-compose.yml, nginx.conf:
```bash
sudo nano .env
```
далее заполните файл необходимыми параметрами:
```bash
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password 
DB_HOST=db
DB_PORT=5432
SECRET_KEY="SECRET_KEY"
ALLOWED_HOSTS = "IP"
```
Сохраните настройки ctrl+O и выйдите из редактора Nano ctrl+X

### Установка docker, docker-compose, PostgreSQL на сервер
Для успешного запуска предварительно должны быть установлены:
docker:
```bash
sudo apt install docker.io 
```
docker-compose:
```bash
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```
PostgreSQL:
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib -y
```
### Настройки для Workflow :
- проверка кода на PEP8
- сборка и публикация последней версии образа docker на dockerhub
- автоматический deploy на сервер
- уведомление в Telegram о завершении Workflow 

Для работы Workflow добавьте переменные окружения в Secrets GitHub:
```bash
DB_ENGINE: django.db.backends.postgresql
DB_HOST: db
DB_NAME: postgres
DB_PORT: 5432
DOCKER_USERNAME: логин
DOCKER_PASSWORD: пароль
HOST: публичный IP сервера
USER: username сервера
PASSPHRASE: пароль для подключения к серверу по ssh(если установлен)
SSH_KEY: локальный ключ ssh
POSTGRES_PASSWORD: postgres
POSTGRES_USER: postgres
TELEGRAM_TO: токен пользователя (получить в userinfobot)
TELEGRAM_TOKEN: токен Вашего бота (получить в BotFather)
```

## Запуск проекта на сервере
Убедитесь, что образы проекта доступны:
```bash
sudo docker image ls -a
```
Пример:
```bash
caveinfix/foodgram_front   latest    01e95d601dd3   21 hours ago    301MB
caveinfix/foodgram_back    <none>    f526fa76bcf0   21 hours ago    286MB
```
Если образы отсутствуют, выполните команды:
```bash
sudo docker pull caveinfix/foodgram_back:latest
sudo docker pullcaveinfix/foodgram_front:latest
```
## Запуск docker-compose
Выполните команду:
```bash
sudo docker-compose up -d --build
```
Далее необходимо собрать статику и выполнить миграции:
```bash
sudo docker-compose exec backend python manage.py collectstatic --noinput
sudo docker-compose exec backend python manage.py migrate --noinput
```
## Наполнение базы тестовыми данными
Чтобы быстро посмотреть функционал проекта сделан дамп БД, загрузить его можно по команде:
```bash
sudo docker-compose exec -T backend python manage.py loaddata dump.json
```
Также Вы можете самостоятельно наполнить БД первоначальными данными, перейдите в контейнер командой:
```bash
sudo docker exec -it <CONTAINER ID> bash
```
Узнать CONTAINER ID - name backend:
```bash
sudo docker container ls -a
```
Импортируйте из CSV данные с ингредиентами:
```bash
python manage.py import_csv
```
Создайте суперпользователя:
```bash
python manage.py createsuperuser
```

### REST API
Подробная документация API доступна по ссылке - http://fgram.ddns.net/api/docs/

Пример эндпоинтов:
#### Регистрация пользователя

```http
  POST http://fgram.ddns.net/api/users/
```
Запрос:
```bash
{
    "username":"user",
    "email":"user@gmail.com",
    "first_name":"Name",
    "last_name":"Lastname",
    "password":"TestPassword123"
}
```


#### Авторизация и получение токена

```http
 GET http://fgram.ddns.net/api/auth/token/login/
```
Запрос:
```bash
{
    "email":"user@gmail.com",
    "password":"TestPassword123"
}
```
Ответ:
```bash
{
    "auth_token": "091c52cce8f90c24bcc4ddccc1974e7713ea483e"
}
```


## Автор проекта

Филипп [@caveinfix](https://github.com/caveinfix)
e-mail: caveinfix@gmail.com


