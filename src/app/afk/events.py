from datetime import datetime

import discord
from discord.ext import commands

import config

from .models import (
    check_and_reply,
    format_duration,
    get_afk_user,
    remove_afk,
    remove_afk_nickname,
)


def setup_afk_events(bot: commands.Bot):
    @bot.event
    async def on_message(message: discord.Message):
        if message.author.bot or not message.guild:
            return

        guild_id = message.guild.id
        for entity in message.mentions:
            row = get_afk_user(entity.id, guild_id)
            if not row or not check_and_reply(message.author.id, entity.id):
                continue

            afk_since = datetime.fromisoformat(row["afk_since"])
            duration = format_duration(int((datetime.now() - afk_since).total_seconds()))
            reply = config.AFK_AUTO_REPLY.format(
                mention=entity.mention,
                reason=row.get("afk_reason") or "Отошёл",
                duration=duration,
            )
            await message.channel.send(reply, delete_after=60)

        await bot.process_commands(message)

    @bot.event
    async def on_voice_state_update(
        member: discord.Member, before: discord.VoiceState, after: discord.VoiceState
    ):
        if after.channel is None or before.channel is not None:
            return
        if not get_afk_user(member.id, member.guild.id):
            return

        await remove_afk_nickname(member)
        remove_afk(member.id, member.guild.id)
        channel = member.guild.system_channel
        if not channel and member.guild.text_channels:
            channel = member.guild.text_channels[0]
        if channel:
            embed = discord.Embed(
                title=config.AFK_VOICE_RETURN_TITLE.format(user=member.display_name),
                description=config.AFK_VOICE_RETURN_DESC,
                color=discord.Color.green(),
            )
            await channel.send(embed=embed, delete_after=30)
