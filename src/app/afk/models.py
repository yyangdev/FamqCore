from datetime import datetime
from typing import Any

import discord

from database.afk_db import (
    check_cooldown as db_check_cooldown,
    get_afk_user as db_get_afk_user,
    get_all_afk as db_get_all_afk,
    get_user_stats as db_get_user_stats,
    remove_afk as db_remove_afk,
    set_afk as db_set_afk,
    set_cooldown as db_set_cooldown,
    update_stats_on_remove,
    update_stats_on_set,
)


def set_afk(user_id: int, guild_id: int, reason: str, estimated_return: str | None = None) -> None:
    now = datetime.now().isoformat()
    db_set_afk(user_id, guild_id, reason, now, estimated_return)
    update_stats_on_set(user_id)


def remove_afk(user_id: int, guild_id: int) -> int | None:
    row = db_get_afk_user(user_id, guild_id)
    if not row:
        return None
    afk_since = datetime.fromisoformat(row["afk_since"])
    duration = int((datetime.now() - afk_since).total_seconds())
    db_remove_afk(user_id, guild_id)
    update_stats_on_remove(user_id, duration)
    return duration


def get_afk_user(user_id: int, guild_id: int) -> dict[str, Any] | None:
    row = db_get_afk_user(user_id, guild_id)
    if not row:
        return None
    return dict(row)


def get_all_afk(guild_id: int) -> list[dict[str, Any]]:
    rows = db_get_all_afk(guild_id)
    return [dict(row) for row in rows]


def check_and_reply(mentioner_id: int, afk_user_id: int) -> bool:
    if db_check_cooldown(mentioner_id, afk_user_id, 30):
        db_set_cooldown(mentioner_id, afk_user_id)
        return True
    return False


def get_user_stats(user_id: int) -> dict[str, Any] | None:
    row = db_get_user_stats(user_id)
    if not row:
        return None
    return dict(row)


async def add_afk_nickname(member: discord.Member) -> bool:
    if member.nick and "[AFK]" in member.nick:
        return True
    new_nick = f"[AFK] {member.display_name}"[:32]
    try:
        await member.edit(nick=new_nick)
        return True
    except discord.Forbidden:
        return False


async def remove_afk_nickname(member: discord.Member) -> bool:
    if not member.nick or "[AFK]" not in member.nick:
        return True
    new_nick = member.nick.replace("[AFK] ", "", 1).replace("[AFK]", "", 1)[:32]
    try:
        await member.edit(nick=new_nick or None)
        return True
    except discord.Forbidden:
        return False
