# Деплой

Запуск в бою и всё, что с этим связано: Docker, данные, бэкапы, обновления.

## Docker Compose (рекомендуемый способ)

```bash
cp src/app/.env.example src/app/.env   # вписать токен
docker compose up -d
```

Compose-файл маленький:

- один сервис `bot` с `restart: unless-stopped`,
- `.env` берётся из `src/app/.env`,
- база лежит в volume `bot_data`, логи - в `bot_logs`.

Управление:

```bash
docker compose logs -f      # смотреть логи
docker compose restart      # перезапуск
docker compose down         # остановить
docker compose up -d --build   # пересобрать и запустить
```

## Голый Docker

```bash
docker build -t regent-bot .
docker run -d --name regent-bot --env-file src/app/.env regent-bot
```

Без volumes данные умрут вместе с контейнером, так что для прода лучше compose.

## Где что лежит внутри контейнера

| Путь | Что |
|------|-----|
| `/app` | Код |
| `/app/database/database.db` | База SQLite (volume) |
| `/app/logs/bot.log` | Логи (volume) |

## Безопасность контейнера

Контейнер запускается от непривилегированного пользователя `botuser`. В него не
копируются тесты и секреты, включены `PYTHONUNBUFFERED` и Docker healthcheck.
При старте бот валидирует конфигурацию и наличие `TOKEN`; без корректного
`.env` процесс завершится с ошибкой. Тесты выполняются в CI до деплоя.

## Обновление версии

```bash
git pull
docker compose up -d --build
```

Схема базы управляется встроенными SQLite-миграциями через `PRAGMA user_version`. При старте бот применяет недостающие миграции автоматически; перед обновлением production всё равно сделайте бэкап `database.db`.

## Бэкап и восстановление

В репозитории есть `scripts/backup.sh`. Запускайте его по cron на хосте, где
смонтирован volume, например:

```bash
DB_PATH=/srv/regent/database.db BACKUP_DIR=/srv/regent/backups RETENTION=14 \
  ./scripts/backup.sh
```

Скрипт использует SQLite online backup API, поэтому копия консистентна даже при
работающем боте, и оставляет последние 14 файлов. Для восстановления остановите
бота, сохраните повреждённый файл, замените `database.db` копией и запустите
compose снова. После восстановления проверьте логи миграций.

## Логи

Два потока: `docker compose logs` и файл `logs/bot.log` (ротация 3x5 МБ). При странном поведении бота первым делом смотрите оба.

Если что-то совсем развалилось - пишите с куском лога: Discord **yangblya**, Telegram [@yyangov](https://t.me/yyangov).
