from .afk_db import (
    check_cooldown,
    get_afk_user,
    get_all_afk,
    get_user_stats,
    init_afk_db,
    remove_afk,
    set_afk,
    set_cooldown,
    update_stats_on_remove,
    update_stats_on_set,
)
from .tickets_db import (
    delete_ticket,
    get_all_tickets,
    get_stats,
    get_ticket,
    init_db,
    save_ticket,
    update_ticket_status,
)

__all__ = [
    # tickets_db
    "init_db",
    "save_ticket",
    "get_ticket",
    "delete_ticket",
    "update_ticket_status",
    "get_stats",
    "get_all_tickets",
    # afk_db
    "init_afk_db",
    "set_afk",
    "remove_afk",
    "get_afk_user",
    "get_all_afk",
    "check_cooldown",
    "set_cooldown",
    "get_user_stats",
    "update_stats_on_set",
    "update_stats_on_remove",
]
