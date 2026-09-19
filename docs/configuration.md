# Настройка

Все настройки бота - в `src/app/config.py` и `.env`. Идея проекта: менять поведение можно без правки кода.

## .env

| Переменная | Что это | Обязательно |
|------------|---------|-------------|
| `TOKEN` | Токен Discord-бота из Developer Portal | Да |

Больше в `.env` ничего нет. Путь до базы (`DB_PATH`) и до логов (`LOG_DIR`) считаются от папки `src/app` и переопределять их сейчас нельзя - только правкой `config.py`.

## config.py

### Доступы и объекты сервера

| Переменная | Значение по умолчанию | Описание |
|------------|-----------------------|----------|
| `TICKETS_CATEGORY_NAME` | `𝙄𝙣𝙫𝙖𝙞𝙩 𝙁𝙖𝙢𝙞𝙡𝙮` | Категория, куда складываются тикеты |
| `ROLE_APPLIED` | `Подал заявку` | Роль при подаче заявки |
| `ROLE_RECRUITER` | `𝐑𝐞𝐜𝐫𝐮𝐢𝐭👨🏻‍💻` | Роль рекрутёра, пингуется в новых тикетах |
| `ROLE_OWNER` | `𝙊𝙬𝙣𝙚𝙧👑` | Владелец, доступ к тикетам и пинг |
| `ROLE_DEP_OWNER` | `𝘿𝙚𝙥.O𝙬𝙣𝙚𝙧⭐` | Зам. владельца, то же |
| `ROLE_ADMIN` | `Admin` | Доступ к тикетам |
| `ROLE_SUPPORT` | `Support` | Доступ к тикетам |
| `LOG_CHANNEL_NAME` | `📋ᥙᴛ᧐ᴦᥙ-ɜᥲяʙ᧐κ` | Канал с логом решений |
| `VOICE_CHANNELS` | `["🔊Обзвон 1", "🔊Обзвон 2", "🔊Обзвон 3"]` | Голосовые каналы для кнопки обзвона |

Внимание: поиск идёт по имени. Если переименуете роль или канал на сервере - бот их не найдёт. Переход на ID запланирован (issue #62).

### Команды

| Переменная | Значение | Описание |
|------------|----------|----------|
| `CMD_PREFIX` | `!` | Префикс команд |
| `CMD_REGENT` | `regent` | Панель подачи заявки |
| `CMD_STATS` | `stats` | Статистика заявок |
| `CMD_HISTORY` | `history` | История заявок |

### Тексты заявок

| Переменная | Описание |
|------------|----------|
| `DM_MESSAGE` | Личное сообщение после подачи заявки |
| `TICKET_RP_TITLE` | Заголовок RP-формы |
| `TICKET_CAPT_TITLE` | Заголовок CAPT-формы |
| `REGENT_EMBED_TITLE` | Заголовок панели `!regent` |
| `REGENT_EMBED_DESCRIPTION` | Текст панели: правила, требования к откатам |
| `ACCEPT_EMBED_TITLE` | Заголовок записи в логе при принятии |
| `DENY_EMBED_TITLE` | Заголовок записи в логе при отказе |
| `ERROR_TICKET_CREATE` | Сообщение при сбое создания тикета |

### Поля форм RP_FIELDS и CAPT_FIELDS

Каждое поле - кортеж из четырёх значений:

```python
("Никнейм в игре + статик", "Ваш игровой ник и статик (если есть)", True, 100)
#  ^label                     ^placeholder                             ^required ^max_length
```

Жёсткие лимиты Discord, выход за которые сломает форму:

- полей в форме - максимум **5** (issue #55)
- `label` - максимум **45** символов. Сейчас в RP-форме одно поле 52 символа, поэтому кнопка RP падает - открыт issue #79, до его исправления RP не работает
- `placeholder` - максимум **100** символов
- `max_length` - от 1 до 4000

Поля с `max_length` больше 150 вводаются многострочным полем, остальные - однострочным.

### Настройки AFK

| Переменная | Значение | Описание |
|------------|----------|----------|
| `AFK_COOLDOWN_SECONDS` | `30` | Кулдаун автоответа на упоминание для пары «кто упомянул - кто в AFK» |
| `AFK_NICK_PREFIX` | `[AFK] ` | Префикс ника у AFK-пользователя |

Все тексты AFK тоже в конфиге, группа `AFK_*`:

| Группа | Переменные |
|--------|-----------|
| Заголовки | `AFK_EMBED_TITLE`, `AFK_EMBED_DESCRIPTION`, `AFK_MENU_TITLE`, `AFK_MENU_NO_AFK`, `AFK_MENU_TOTAL` |
| Модальное окно взятия | `AFK_MODAL_TITLE`, `AFK_MODAL_REASON_LABEL`, `AFK_MODAL_REASON_PLACEHOLDER`, `AFK_MODAL_DURATION_LABEL`, `AFK_MODAL_DURATION_PLACEHOLDER` |
| Окно возврата | `AFK_RETURN_MODAL_TITLE`, `AFK_RETURN_CONFIRM`, `AFK_RETURN_DURATION_LABEL` |
| Кнопки | `AFK_BUTTON_LEAVE`, `AFK_BUTTON_RETURN`, `AFK_BUTTON_REFRESH`, `AFK_BUTTON_STAY` |
| Сообщения | `AFK_RETURN_SUCCESS`, `AFK_RETURN_STAY`, `AFK_RETURN_ERROR`, `AFK_NOT_AFK`, `AFK_INVALID_USER`, `AFK_REASON_DEFAULT` |
| Статус и проверка | `AFK_AFK_STATUS`, `AFK_CHECKED_NOT_AFK` |
| Статистика | `AFK_STATS_TITLE`, `AFK_STATS_NO_DATA`, `AFK_STATS_TOTAL`, `AFK_STATS_TOTAL_TIME`, `AFK_STATS_LONGEST` |
| Автоответ | `AFK_AUTO_REPLY` - шаблон с `{mention}`, `{reason}`, `{duration}` |
| Возврат через голос | `AFK_VOICE_RETURN_TITLE` (шаблон с `{user}`), `AFK_VOICE_RETURN_DESC` |

## Примеры правок

Сменить префикс команд:

```python
CMD_PREFIX = "."
```

Сменить кулдаун автоответа на минуту:

```python
AFK_COOLDOWN_SECONDS = 60
```

Добавить поле в CAPT-форму (помним: максимум 5 полей, label до 45 символов):

```python
CAPT_FIELDS = [
    ...
    ("Опыт в каптах", "Сколько заходов сыграли", False, 100),
]
```

## Когда бот подхватывает изменения

Только при перезапуске. Конфиг читается один раз при импорте модулей.
