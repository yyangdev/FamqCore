from datetime import datetime

import discord
from discord.ext import commands

import config

from .models import (
    check_and_reply,
    format_duration,
    get_afk_user,
)


def setup_afk_events(bot: commands.Bot):
    """События AFK.

    По спецификации активность пользователя НЕ влияет на его AFK:
    статус держится, пока не истечёт время (см. afk/tasks.py),
    либо пока его не снимет модератор (!afk_remove) или сам пользователь
    кнопкой «Отменить AFK». Обработчика on_voice_state_update здесь
    намеренно нет — голосовая активность AFK не снимает.
    """

    @bot.event
    async def on_message(message: discord.Message):
        if message.author.bot or not message.guild:
            return

        guild_id = message.guild.id

        # команды (!afk_check @user) не должны триггерить автоответ про AFK
        if not message.content.startswith(config.CMD_PREFIX) and not message.reference:
            replies = []
            for entity in message.mentions:
                row = get_afk_user(entity.id, guild_id)
                if not row or not check_and_reply(message.author.id, entity.id, guild_id):
                    continue

                afk_since = datetime.fromisoformat(row["afk_since"])
                duration = format_duration(int((datetime.now() - afk_since).total_seconds()))
                replies.append(
                    config.AFK_AUTO_REPLY.format(
                        # Do not ping an AFK user a second time.
                        mention=entity.display_name,
                        reason=row.get("afk_reason") or "Отошёл",
                        duration=duration,
                    )
                )
            if replies:
                try:
                    await message.channel.send(
                        "\n\n".join(replies),
                        delete_after=60,
                        allowed_mentions=discord.AllowedMentions.none(),
                    )
                except discord.Forbidden:
                    return

        await bot.process_commands(message)
