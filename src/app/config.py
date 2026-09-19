import os

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
DB_PATH = os.path.join(os.path.dirname(__file__), "database", "database.db")
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")

# Категория для создания тикетов
TICKETS_CATEGORY_NAME = "𝙄𝙣𝙫𝙖𝙞𝙩 𝙁𝙖𝙢𝙞𝙡𝙮"

# Роли
ROLE_APPLIED = "Подал заявку"  # выдается при создание тикета
ROLE_RECRUITER = "𝐑𝐞𝐜𝐫𝐮𝐢𝐭👨🏻‍💻"
ROLE_OWNER = "𝙊𝙬𝙣𝙚𝙧👑"
ROLE_DEP_OWNER = "𝘿𝙚𝙥.O𝙬𝙣𝙚𝙧⭐"
ROLE_ADMIN = "Admin"
ROLE_SUPPORT = "Support"

# Каналы
LOG_CHANNEL_NAME = "📋ᥙᴛ᧐ᴦᥙ-ɜᥲяʙ᧐κ"
VOICE_CHANNELS = ["🔊Обзвон 1", "🔊Обзвон 2", "🔊Обзвон 3"]

# Команды
CMD_PREFIX = "!"
CMD_REGENT = "regent"
CMD_STATS = "stats"
CMD_HISTORY = "history"

# Тексты
DM_MESSAGE = "Вы подали заявку в клуб Regent, ожидайте — скоро её рассмотрят ⏳."

TICKET_RP_TITLE = "RP ЗАЯВКА"
TICKET_CAPT_TITLE = "CAPT ЗАЯВКА"

REGENT_EMBED_TITLE = "Regent FAMQ"
REGENT_EMBED_DESCRIPTION = (
    "Путь в семью Regent начинается здесь!\n\n"
    "Заявки принимаются только на сервере Orlando.\n"
    "Уведомление о приглашении на обзвон отправляется в ваш тикет.\n\n"
    "**Срок рассмотрения:** до 24 часов.\n"
    "**Важно:** неполная заявка будет автоматически ОТКЛОНЕНА.\n\n"
    "**Требования к откатам:**\n"
    "• GG — не более 1 недели (не менее 5 минут).\n"
    "• МП (ВЗЗ, MCL, Capt) — не более 60 дней.\n"
    "• Сайга + спешик/тяжка (по одному на каждый ган).\n\n"
    "**Нарушение условий = автоматический отказ.**"
)
RP_FIELDS = [
    ("Никнейм в игре + статик", "Ваш игровой ник и статик (если есть)", True, 100),
    ("OOC имя и возраст(IRL)", "Ваше реальное имя и возраст", True, 100),
    ("Семьи в которых вы состояли", "Перечислите все семьи, и почему ушли?", True, 300),
    ("Почему именно наша семья", "Ваша мотивация", True, 500),
    (
        "Средний онлайн в день (Пример:5 часов - 12:00-17:00)",
        "Сколько часов играете / в какое время",
        True,
        100,
    ),
]

CAPT_FIELDS = [
    ("Никнейм в игре", "Ваш игровой ник", True, 50),
    ("Статик", "Ваш статик", False, 50),
    ("OOC имя и возраст", "Ваше реальное имя и возраст", True, 100),
    ("Откат сайга и спешик 2+ минуты гангейм", "Ваши откаты", True, 200),
    ("Откаты MCL каптов и МП", "Ваши откаты в MCL", False, 200),
]

ACCEPT_EMBED_TITLE = "✅ Заявка принята, добро пожаловать в семью"
DENY_EMBED_TITLE = "❌ ЗАЯВКА ОТКЛОНЕНА"

ERROR_GENERIC = "Произошла ошибка. Попробуйте позже."
ERROR_TICKET_CREATE = "Не удалось создать заявку. Попробуйте позже."

# AFK Система
AFK_CMD_NAME = "AFK"
AFK_LIST_CMD = "afk_list"
AFK_CHECK_CMD = "afk_check"
AFK_STATS_CMD = "afk_stats"

AFK_EMBED_TITLE = "**🔴 AFK Система**"
AFK_EMBED_DESCRIPTION = "Используй кнопки ниже для управления статусом AFK"
AFK_MENU_TITLE = "Во время AFK вам не будут выдавать высказываения по причине НВС"
AFK_MENU_NO_AFK = "В АФК никого нет."
AFK_MENU_TOTAL = "Всего в АФК"

# установка AFK
AFK_MODAL_TITLE = "Установка AFK"
AFK_MODAL_REASON_LABEL = "📝 Причина"
AFK_MODAL_REASON_PLACEHOLDER = "🔴 Взять AFK"
AFK_MODAL_DURATION_LABEL = "⏰ На сколько?"
AFK_MODAL_DURATION_PLACEHOLDER = "1 час, 2 часа, 3 часа, 23:45, через 30 мин"

AFK_RETURN_MODAL_TITLE = "Возвращение из AFK"

AFK_BUTTON_LEAVE = "🔴 Взять AFK"
AFK_BUTTON_RETURN = "🟢 Отменить AFK"
AFK_BUTTON_REFRESH = "📋 Список AFK"
AFK_BUTTON_STAY = "❌ Остаюсь"

AFK_REASON_DEFAULT = "🔴 Взять AFK"

AFK_RETURN_CONFIRM = "Вы уверены, что хотите снять AFK статус?"
AFK_RETURN_DURATION_LABEL = "Ты отсутствовал"

AFK_RETURN_SUCCESS = "✅ Вы вернулись!"
AFK_RETURN_STAY = "❌ Вы остались в AFK."
AFK_RETURN_ERROR = "Ошибка: AFK статус не найден."
AFK_NOT_AFK = "Вы не находитесь в AFK."
AFK_INVALID_USER = "Это не ваше меню."

AFK_AFK_STATUS = "🔴 В АФК"
AFK_CHECKED_NOT_AFK = "✅ Этот пользователь не в AFK"

AFK_STATS_TITLE = "📊 AFK Статистика"
AFK_STATS_NO_DATA = "📊 Статистика AFK: пользователь ещё не использовал AFK"

AFK_STATS_TOTAL = "Всего уходов в AFK"
AFK_STATS_TOTAL_TIME = "Общее время в AFK"
AFK_STATS_LONGEST = "Самая долгая сессия"

AFK_AUTO_REPLY = "{mention} **в AFK**\nПричина: {reason}\nУшёл: {duration} назад"

AFK_VOICE_RETURN_TITLE = "{user} вернулся!"
AFK_VOICE_RETURN_DESC = "🟢 Пользователь вернулся из AFK (вошёл в голосовой канал)"

AFK_COOLDOWN_SECONDS = 30
AFK_NICK_PREFIX = "[AFK] "
