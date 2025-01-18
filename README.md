# Prof Map
### Инструкция по запуску
#### Требования 
* [Python 3.11.9](https://www.python.org/downloads/release/python-3119/)
* [PostgreSQL](https://www.postgresql.org/)
#### Шаги по запуску
0. Установить технологии из требований
1. Подготовка базы данных

Необходимо создать базу данных в PostgreSQL и запустить в ней скрипты, расположенные в [database/migrations](https://github.com/DelicaLib/prof-map/tree/main/database/migrations). После создания понадобятся следующие данные:
* Хост, на котором развёрнут postgres
* Порт, на котором развёрнут postgres
* Имя пользователя бд
* Пароль к бд
* Имя бд

2. Получение ключа для работы с GPT.

Поскольку нет возможности адекватно получить API ключ для ChatGPT, используется сервис [ProxyAPI](https://proxyapi.ru/). На нём необходимо зарегистрироваться, пополнить баланс и получить API ключ.

3. Настройка секретов

Для хранения секретов используется сервис [Doppler](https://www.doppler.com/). Для работы необходимо: 
* Зарегистрироваться/авторизоваться
* Создать проект под названием *prof-map*
* Добавить следующие секреты в *dev*
  * *DB_HOST* - Хост, на котором развёрнут postgres
  * *DB_PORT* - Порт, на котором развёрнут postgres
  * *DB_USER* - Имя пользователя бд
  * *DB_PASSWORD* - Пароль к бд
  * *DB_NAME* - Имя бд
  * *GPT_API_KEY* - API ключ для [ProxyAPI](https://proxyapi.ru/)
* Получить API token [Doppler](https://www.doppler.com/)
4. Установка Python зависимостей

Рекомендуем создать [виртуальное окружение](https://docs.python.org/3/library/venv.html) в корне репозитория.
Далее, для установки зависимостей, в корне репозитория выполнить следующую команду:
```bash
pip install -r requirements.txt
```
5. Запуск бэкенда

Для того, чтобы запустить бэкенд, необходимо перейти в директорию [backend](https://github.com/DelicaLib/prof-map/tree/main/backend):
```bash
cd backend
```
После этого можно запустить бэкенд командой:
```bash
DOPPLER_TOKEN=*your token* python main.py --config config.toml
```
Где:
* *DOPPLER_TOKEN* - переменная окружения, в которой будет хранится ваш токен для [Doppler](https://www.doppler.com/)
* *--config* - обязательный параметр запуска, в котором указывает относительный путь до конфигурационного файла. В нашем случае [config.toml](https://github.com/DelicaLib/prof-map/blob/main/backend/config.toml)

6. Проверка успешности запуска

Дожидаемся успешной загрузки всех моделей и переходим по адресу *http://host:port/docs*, где host - адрес хоста, на котором запущен бэкенд (скорее всего, у вас это будет localhost), а port - порт, указанный в [config.toml](https://github.com/DelicaLib/prof-map/blob/main/backend/config.toml) как *port* (8000 по умолчанию). В нашем случае получается *http://localhost:8000/docs*.