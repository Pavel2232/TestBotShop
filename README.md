Тестовое задание:
Ниже представлено описание проекта и его основных функциональных возможностей:

# Каталог товаров

## Категории и подкатегории товаров
- Реализуются в формате инлайн кнопок с пагинацией.

## Товары
- Представлены в формате: фото, описание.
- Доступны кнопки для добавления в корзину, указания количества и подтверждения заказа.

# Корзина

## Просмотр корзины
- Позволяет просматривать товары, добавленные в корзину.
- Дает возможность удалить товар из корзины.
- Предоставляет возможность ввести данные для доставки.
- Имеет интеграцию с платежными шлюзами Tinkoff или ЮKassa для осуществления платежей.

# FAQ (Ответы на частозадаваемые вопросы)

- Ответы на частозадаваемые вопросы представлены в формате инлайн режима с автоматическим дополнением вопроса.

# Дополнительные функциональности

- Все заказы автоматически сохраняются в Excel таблицу для последующей обработки.
- Реализована административная панель на Django со следующими функциями:
  - Таблица всех клиентов.
  - Возможность проведения рассылок клиентам.

# Команды и функции бота

- /start - Проверка на подписку группы и канала.

Это описание включает основные возможности и функциональности вашего проекта. При желании вы можете расширить его и добавить дополнительные детали в зависимости от специфики вашего приложения.
# Как запустить:
* склонируйте репозиторий ``` git clone https://github.com/Pavel2232/TestBotShop```
* установите зависимости проекта ```poetry install ```
* заполните .env
* 
````dotenv
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=
SECRET_KEY=
DATABASE_URL=
TG_TOKEN_BOT=
REDIS_HOST=
REDIS_PORT=
REDIS_DATABASES=
REDIS_URL=
CHANEL_ID=канала в тг
GROUP_ID=группы в тг
DEFAULT_PAGINATION=число разбивки 
FILE_NAME=названгие excel файла
````
* поднимите тестувую базу данных(если есть необходимостьв ней)
```docker
docker-compose up -d
```


## Навигация по проекту:
- есть файл для тестирования с уже готовыми данными для бд
````python
./manage.py loaddata db.json
````


