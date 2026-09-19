# Regent Famq Bot

Discord-бот для игровой семьи Regent на проекте Majestic RP. Принимает заявки на вступление, ведёт учёт AFK-статусов и статистику по рекрутингу.

> **Проект в бета-стадии.** Мы только начинаем активную разработку и ищем помощников: разработчиков на Python, тестировщиков и просто людей с идеями. Хотите помочь - пишите, контакты ниже.

## Что умеет бот

- Тикет система с двумя системами заявок рп заявка и капт заявка
- AFK-система: статус с причиной и временем возврата, автоответ на упоминания, статистика
- Команды статистики `!stats` и истории `!history` для администраторов(будет переделанно в веб панель)

## Быстрый старт

```bash
git clone https://github.com/yyangdev/majestick-famq-discord-bot.git
cd majestick-famq-discord-bot/src/app
pip install -r requirements.txt
cp .env.example .env   # вписать токен бота
python main.py
```

Полная инструкция, включая настройку сервера Discord и прав бота: [docs/setup.md](docs/setup.md).

## Документация

| Раздел | О чём |
|--------|-------|
| [Обзор проекта](docs/overview.md) | Для чего бот, статус разработки, планы |
| [Установка и запуск](docs/setup.md) | Пошаговый запуск с нуля |
| [Настройка](docs/configuration.md) | Все переменные config.py и .env |
| [Команды и кнопки](docs/commands.md) | Что и кто может нажимать |
| [AFK-система](docs/afk.md) | Как работает AFK-учёт |
| [Архитектура](docs/architecture.md) | Устройство кода и база данных |
| [Деплой](docs/deployment.md) | Docker, бэкапы, обновления |
| [Тесты и линтер](docs/testing.md) | Как гонять проверки перед PR |
| [Как помочь проекту](docs/contributing.md) | С чего начать новичку в проекте |
| [Дорожная карта](docs/roadmap.md) | Что будем делать дальше |

## Как помочь

Проект в начале пути, любая помощь в цене: от отчёта о баге до готового Pull Request. Список задач - в [Issues](https://github.com/yyangdev/majestick-famq-discord-bot/issues), там есть простые для старта. Подробности в [docs/contributing.md](docs/contributing.md) и [CONTRIBUTING.md](CONTRIBUTING.md).

## Контакты

- Discord: **yangblya**
- Telegram: **[@yyangov](https://t.me/yyangov)**

## Лицензия

MIT. Подробности в [LICENSE](LICENSE).
