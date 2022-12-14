[![codecov](https://codecov.io/gh/painassasin/secure_t/branch/main/graph/badge.svg?token=6joi4dOwKS)](https://codecov.io/gh/painassasin/secure_t)

# Блог с древовидными комментариями
## Стек
- fastapi
- postgres (async)
- alembic

## Описание
### Пользователи
По пользователям ничего интересного - две ручки /auth/signup/, /auth/signin/, причем последняя лжидает форму, а не json.
которые возвращают access_token. Схема аутентификации bearer.

### По постам и комментариям
Раз функциональность у постов и комментариев одна и та же,
решил все в базе хранить как пост.
У поста есть владелец, текст, и id родителя.
При добавлении поста заполняются только владелец и текст, родителя нет.
При добавлении комментариев все то же самое, только еще указывается родитель (верхний пост/комментарий),
под которым написан комментарий.

Например, есть пост A, под ним оставили комментарии
B и C, под комментарием C оставили комментарии D и E,
тогда таблица будет выглядеть так (владельца пропустим):

| id | text | parent_id |
| -- | ---- | --------- |
| 1  |  A   |           |
| 2  |  B   |     1     |
| 3  |  C   |     1     |
| 4  |  D   |     3     |
| 5  |  E   |     3     |

Все ручки и их ответы можно посмотреть с [swagger](http://painassasin.ru:9000/docs/).
Для обновления и удаления комментариев ручки делать не стал, т.к. они удаляются так же,
как и посты (/blog/posts/{post_id}/). GET ручки на комментарии не вижу смысла делать, даже
не представляю как их использовать).

### Запуск
В корне приложен заполненный env.example файл, его нужно переименовать в .env.
```shell
docker-compose up -d db
alembic upgrade head
uvicorn backend.app:app --reload
```
либо в контейнере
```shell
docker-compose build
docker-compose up -d db api
```

### Тесты
```shell
pytest
```
