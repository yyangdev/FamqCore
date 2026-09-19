from datetime import datetime

import discord
from discord.ext import commands

from .models import (
    get_afk_user,
    get_all_afk,
    get_user_stats,
)
from .views import AfkMenuView


def format_duration(seconds: int) -> str:
    hours, remainder = divmod(seconds, 3600)
    minutes, sec = divmod(remainder, 60)
    parts = []
    if hours:
        parts.append(f"{hours} ч")
    if minutes:
        parts.append(f"{minutes} мин")
    if sec or not parts:
        parts.append(f"{sec} сек")
    return " ".join(parts)


class AfkCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="afk")
    async def afk_command(self, ctx: commands.Context):
        embed = discord.Embed(
            title="🔴 AFK Система",
            description="Используй кнопки ниже для управления статусом AFK",
            color=discord.Color.red(),
        )
        await ctx.send(embed=embed, view=AfkMenuView())

    @commands.command(name="afk_list")
    async def afk_list_command(self, ctx: commands.Context):
        rows = get_all_afk(ctx.guild.id)
        if not rows:
            embed = discord.Embed(
                title="🔴 AFK Список",
                description="В АФК никого нет.",
                color=discord.Color.green(),
            )
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(
            title="🔴 ЛЮДИ НАХОДЯЩИЕСЯ В АФК",
            color=discord.Color.red(),
        )
        embed.add_field(name="Всего в АФК", value=f"{len(rows)} человек", inline=False)

        lines = []
        for idx, row in enumerate(rows, 1):
            member = ctx.guild.get_member(row["user_id"])
            name = member.mention if member else f"<@{row['user_id']}>"
            reason = row.get("afk_reason") or "Отошёл"
            afk_since = datetime.fromisoformat(row["afk_since"])
            since_str = afk_since.strftime("%H:%M")
            return_str = "—"
            if row.get("estimated_return"):
                try:
                    ret = datetime.fromisoformat(row["estimated_return"])
                    return_str = ret.strftime("%H:%M")
                except Exception:
                    return_str = str(row["estimated_return"])[:20]
            lines.append(
                f"{idx}) {name} | Причина: {reason}    Ушел: {since_str} | Вернется: {return_str}"
            )

        embed.description = "\n".join(lines)
        await ctx.send(embed=embed)

    @commands.command(name="afk_check")
    async def afk_check_command(self, ctx: commands.Context, member: discord.Member):
        row = get_afk_user(member.id, ctx.guild.id)
        if not row:
            embed = discord.Embed(
                title=f"{member.display_name}",
                description="✅ Этот пользователь не в AFK",
                color=discord.Color.green(),
            )
            await ctx.send(embed=embed)
            return

        afk_since = datetime.fromisoformat(row["afk_since"])
        duration = datetime.now() - afk_since
        duration_str = format_duration(int(duration.total_seconds()))
        reason = row.get("afk_reason") or "Отошёл"

        embed = discord.Embed(
            title=f"{member.display_name}",
            color=discord.Color.orange(),
        )
        embed.add_field(name="Статус", value="🔴 В АФК", inline=False)
        embed.add_field(name="Причина", value=reason, inline=False)
        embed.add_field(name="Ушёл", value=afk_since.strftime("%H:%M"), inline=True)
        embed.add_field(name="Время в AFK", value=duration_str, inline=True)

        await ctx.send(embed=embed)

    @commands.command(name="afk_stats")
    async def afk_stats_command(self, ctx: commands.Context, member: discord.Member):
        stats = get_user_stats(member.id)
        if not stats:
            embed = discord.Embed(
                title=f"{member.display_name}",
                description="📊 Статистика AFK: пользователь ещё не использовал AFK",
                color=discord.Color.blue(),
            )
            await ctx.send(embed=embed)
            return

        def fmt_secs(seconds: int) -> str:
            hours, remainder = divmod(seconds, 3600)
            minutes, sec = divmod(remainder, 60)
            parts = []
            if hours >= 24:
                days = hours // 24
                hours = hours % 24
                parts.append(f"{days} дн")
            if hours:
                parts.append(f"{hours} ч")
            if minutes:
                parts.append(f"{minutes} мин")
            if sec or not parts:
                parts.append(f"{sec} сек")
            return " ".join(parts)

        embed = discord.Embed(
            title=f"📊 AFK Статистика: {member.display_name}",
            color=discord.Color.blue(),
        )
        embed.add_field(name="Всего уходов в AFK", value=stats["total_afk_count"], inline=True)
        embed.add_field(
            name="Общее время в AFK", value=fmt_secs(stats["total_afk_seconds"]), inline=True
        )
        embed.add_field(
            name="Самая долгая сессия", value=fmt_secs(stats["longest_afk_seconds"]), inline=False
        )

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(AfkCog(bot))
