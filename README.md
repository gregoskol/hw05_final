# YaTube
## _Социальная сеть для блогеров_

## Описание:
Социальная сеть с возможностью регистрации, созданий постов, групп, комментариев, подписок на понравившихся авторов и группы. 
В реализации используются пагинация и кеширование. Написаны тесты, проверяющие работу сервиса.

Авторизованные пользователи могут:
* Просматривать, публиковать, удалять и редактировать свои публикации;
* Просматривать информацию о сообществах;
* Просматривать и публиковать комментарии от своего имени к публикациям других пользователей, удалять и редактировать свои комментарии;
* Подписываться на других пользователей и просматривать свои подписки.

## Установка:
1. Клонируйте репозиторий, перейдите в него:
```sh
git clone git@github.com:gregoskol/hw05_final.git
cd hw05_final
```
2. Создайте и активируйте виртуальное окружение:
```sh
python -m venv venv
source venv/Scripts/activate
```
3. Установите зависимости:
```sh
python -m pip install --upgrade pip
pip install -r requirements.txt
```
4. Перейдите в папку yatube, выполните миграции, запустите проект:
```sh
cd yatube
python manage.py migrate
python manage.py runserver
```