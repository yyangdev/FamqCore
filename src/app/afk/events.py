import discord
from discord.ext import commands

from .models import check_and_reply, get_afk_user, remove_afk, remove_afk_nickname


def setup_afk_events(bot: commands.Bot):
    @bot.event
    async def on_message(message: discord.Message):
        if message.author.bot:
            return

        guild_id = message.guild.id if message.guild else None
        if not guild_id:
            return

        mentions = []
        for entity in message.mentions:
            row = get_afk_user(entity.id, guild_id)
            if row:
                mentions.append((entity, row))

        if mentions:
            for afk_member, row in mentions:
                if check_and_reply(message.author.id, afk_member.id):
                    afk_since = row["afk_since"]
                    from datetime import datetime

                    duration = datetime.now() - datetime.fromisoformat(afk_since)
                    hours, remainder = divmod(int(duration.total_seconds()), 3600)
                    minutes, _ = divmod(remainder, 60)
                    duration_text = f"{hours} ч {minutes} мин" if hours else f"{minutes} мин"
                    reason = row.get("afk_reason") or "Отошёл"

                    reply = (
                        f"{afk_member.mention} **в AFK**\n"
                        f"Причина: {reason}\n"
                        f"Ушёл: {duration_text} назад"
                    )
                    await message.channel.send(reply, delete_after=60)

        await bot.process_commands(message)

    @bot.event
    async def on_voice_state_update(
        member: discord.Member, before: discord.VoiceState, after: discord.VoiceState
    ):
        if after.channel is not None and before.channel is None:
            guild_id = member.guild.id
            row = get_afk_user(member.id, guild_id)
            if row:
                await remove_afk_nickname(member)
                remove_afk(member.id, guild_id)
                channel = member.guild.system_channel
                if not channel and member.guild.text_channels:
                    channel = member.guild.text_channels[0]
                if channel:
                    embed = discord.Embed(
                        title=f"{member.display_name} вернулся!",
                        description="🟢 Пользователь вернулся из AFK (вошёл в голосовой канал)",
                        color=discord.Color.green(),
                    )
                    await channel.send(embed=embed, delete_after=30)
