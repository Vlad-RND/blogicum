### Описание проекта:

Сайт-блог "Blogicum" для размещения публикаций (в т.ч. отложенных) с возможностью комментирования и регистрации.
Каждый пост привязан к категории и локации, по которым осуществляется поиск.

### Используемые библиотеки:

asgiref==3.8.1
Django==5.0.6
django-bootstrap5==24.2
pillow==10.3.0
python-dotenv==1.0.1
setuptools==69.2.0
sqlparse==0.4.4
tzdata==2024.1
wheel==0.43.0

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/Vlad-RND/blogicum.git
```

```
cd blogicum
```

Cоздать и активировать виртуальное окружение:

```
python -m venv env
```

```
source venv/Scripts/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python manage.py runserver
```

### Функционал:

- Регистрация;
- Создание/удаление/редактирование поста;
- Отложенная публикация поста;
- Комментирование публикации;
- Личный кабинет пользователя с публикациями.

Автор - Vlad-RND,
GIT - https://github.com/Vlad-RND
