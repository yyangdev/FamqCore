# Архитектура

Как устроен код. Читается за десять минут, кодовая база небольшая - около 1500 строк с тестами.

## Общая схема

Бот - обычное приложение на discord.py 2.x с префиксными командами. Вход - `main.py`, логика разбита на три модуля предметной области плюс два служебных:

```
src/app/
├── main.py              - точка входа: интенты, on_ready, прогон тестов, запуск
├── config.py            - все настройки и тексты
├── requirements.txt
├── .env.example
│
├── database/            - слой данных, голый sqlite3
│   ├── db.py            - get_db(): открыть соединение
│   ├── tickets_db.py    - таблицы tickets и stats, CRUD
│   └── afk_db.py        - таблицы afk_users/afk_cooldown/afk_stats
│
├── tickets/             - заявки
│   ├── commands.py      - !regent, !stats, !history + панель типов заявок
│   ├── create_ticket.py - форма TicketModal и создание тикета
│   ├── decision.py      - кнопки и форма «Принять»/«Отказать» (тип = Decision)
│   ├── call_voice.py    - вызов на обзвон
│   ├── close_ticket.py  - закрытие тикета
│   └── views.py         - FullTicketView, собирает все кнопки
│
├── afk/                 - AFK
│   ├── commands.py      - !afk, !afk_list, !afk_check, !afk_stats
│   ├── events.py        - on_message (автоответ) и on_voice_state_update (снятие)
│   ├── models.py        - бизнес-логика: set/remove, ники, format_duration
│   └── views.py         - меню, формы, build_afk_embed, parse_return_time
│
├── utils/
│   └── logger.py        - логгер: консоль + файл с ротацией
│
└── tests/               - 16 файлов, 234 теста на unittest + mock
```

## Жизненный цикл запуска

1. `main.py` запускает тесты через subprocess. Упали - процесс выходит, бот не стартует (спорное решение, issue #33, но пока так).
2. На событии `on_ready` создаются таблицы (`init_db`, `init_afk_db`) и грузятся расширения `tickets` и `afk` через `bot.load_extension`.
3. Каждое расширение - модуль с функцией `setup(bot)`: ког команд и, у AFK, подписка на события.

## Поток заявки

```
!regent -> TicketTypeView (кнопки RP/CAPT)
        -> TicketModal (5 полей из config)
        -> create_ticket(): роль -> ЛС -> категория -> канал -> запись в БД
        -> FullTicketView в канале тикета
        -> Accept/Deny: DecisionReasonModal -> update_ticket_status -> лог-канал -> удаление канала
```

## Поток AFK-автоответа

```
on_message -> для каждого упомянутого: afk_db.get_afk_user
           -> check_and_reply (кулдаун 30с по паре упомянувший/AFK, таблица afk_cooldown)
           -> ответ в канал с delete_after=60
           -> bot.process_commands (чтобы работали команды)
```

## База данных

Один файл SQLite `src/app/database/database.db`, `row_factory = sqlite3.Row` - строки читаются как словари. Соединение открывается и закрывается на каждый запрос. Это просто, но блокирует цикл событий под нагрузкой, известная задача #37.

### tickets

| Колонка | Тип | Комментарий |
|---------|-----|-------------|
| `id` | INTEGER PK AUTOINCREMENT | |
| `channel_id` | INTEGER UNIQUE | Ключ поиска тикета |
| `user_id` | INTEGER | ID заявителя |
| `user_name` | TEXT | Имя на момент подачи |
| `topic` | TEXT | Заголовок формы |
| `type` | TEXT | `rp` или `capt` |
| `answers` | TEXT | JSON с ответами |
| `status` | TEXT | `open` / `accepted` / `denied`, по умолчанию `open` |
| `created_at` | TEXT | ISO-время |
| `closed_at` | TEXT | ISO-время закрытия |
| `closed_by` | INTEGER | Кто решил |
| `reason` | TEXT | Причина решения |

### stats (дневная сводка)

| Колонка | Тип | Комментарий |
|---------|-----|-------------|
| `id` | INTEGER PK AUTOINCREMENT | |
| `date` | TEXT UNIQUE | День YYYY-MM-DD |
| `total_applications` | INTEGER | Решений за день |
| `accepted` | INTEGER | |
| `denied` | INTEGER | |

### afk_users

| Колонка | Тип | Комментарий |
|---------|-----|-------------|
| `user_id` | INTEGER PK(1) | |
| `guild_id` | INTEGER PK(1) | Пара - первичный ключ, есть индекс по guild_id |
| `afk_reason` | TEXT | По умолчанию «Отошёл» |
| `afk_since` | TEXT | ISO-время старта |
| `estimated_return` | TEXT | Когда обещал вернуться |
| `is_afk` | INTEGER | Всегда 1 - колонка-пережиток, записи просто удаляются при возврате |

### afk_cooldown

Пара (`mentioner_id`, `afk_user_id`) - время последнего автоответа. Не чистится и растёт бесконечно, issue #51.

### afk_stats

`user_id` PK + счётчики: уходов, суммарные секунды, рекорд сессии. Без привязки к серверу, issue #26.

## Принципы, которые держим в коде

- Все тексты и настройки - в `config.py`.
- Один модуль - одна зона ответственности, логика не расползается по импортам.
- Функции маленькие, вложенность до двух уровней.
- Стиль - минимализм: без прослоек «на будущее».

## Известные архитектурные слабости

Честно перечисляем, чтобы новичок не изобретал:

- Бизнес-логика сидит прямо в UI-колбэках - вынос в сервисный слой, issue #97.
- Инициализация в `on_ready` вместо `setup_hook` - гонки, issue #18.
- Синхронный sqlite в асинхронном коде, #37.
- Роли и каналы ищутся по имени, #62.
- Нет привязки tickets/stats к гильдии, #80.
