[![example workflow](https://github.com/caveinfix/foodgram-project-react/actions/workflows/main.yml/badge.svg)](http://fgram.ddns.net/recipes) 

# Проект «Продуктовый помощник» 

Проект — сайт Foodgram, «Продуктовый помощник». Реализован онлайн-сервис и API для него. На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Превью

![App Screenshot](https://i2.paste.pics/a255c4101805a63342e983333a9fe415.png)

## Технологии
[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/) [![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/) [![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat-square&logo=Django%20REST%20Framework)](https://www.django-rest-framework.org/) [![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat-square&logo=PostgreSQL)](https://www.postgresql.org/) [![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat-square&logo=NGINX)](https://nginx.org/ru/) [![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat-square&logo=gunicorn)](https://gunicorn.org/) [![docker](https://img.shields.io/badge/-Docker-464646?style=flat-square&logo=docker)](https://www.docker.com/) [![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat-square&logo=GitHub%20actions)](https://github.com/features/actions) [![Yandex.Cloud](https://img.shields.io/badge/-Yandex.Cloud-464646?style=flat-square&logo=Yandex.Cloud)](https://cloud.yandex.ru/)
## Релиз
Сайт доступен по ссылке: [fgram.ddns.net](http://fgram.ddns.net/recipes) (Временно остановлен)

Документация API: [fgram.ddns.net/api/docs](http://fgram.ddns.net/api/docs/)

Доступ к админке: [fgram.ddns.net/admin/](http://fgram.ddns.net/admin/) (логин: admin@ya.ru, пароль:admin)


## Подготовка к запуску локально
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
Далее заполните файл необходимыми параметрами:
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

Docker:
```bash
sudo apt install docker.io 
```
Docker-compose:
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
- проверка кода по PEP8
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

Frontend: [Yandex-Praktikum](https://github.com/yandex-praktikum/foodgram-project-react)
Дизайн: [Figma](https://www.figma.com/file/HHEJ68zF1bCa7Dx8ZsGxFh/%D0%9F%D1%80%D0%BE%D0%B4%D1%83%D0%BA%D1%82%D0%BE%D0%B2%D1%8B%D0%B9-%D0%BF%D0%BE%D0%BC%D0%BE%D1%89%D0%BD%D0%B8%D0%BA-(Final)?node-id=0%3A1)

Backend: Филипп [@caveinfix](https://github.com/caveinfix)

e-mail: caveinfix@gmail.com


