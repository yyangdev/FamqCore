from datetime import datetime

import discord
from discord.ext import commands

import config

from .models import format_duration, get_afk_user, get_user_stats
from .views import AfkMenuView, build_afk_embed


class AfkCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="afk")
    async def afk_command(self, ctx: commands.Context):
        embed = discord.Embed(
            title=config.AFK_EMBED_TITLE,
            description=config.AFK_EMBED_DESCRIPTION,
            color=discord.Color.red(),
        )
        await ctx.send(embed=embed, view=AfkMenuView())

    @commands.command(name="afk_list")
    async def afk_list_command(self, ctx: commands.Context):
        await ctx.send(embed=build_afk_embed(ctx.guild))

    @commands.command(name="afk_check")
    async def afk_check_command(self, ctx: commands.Context, member: discord.Member):
        row = get_afk_user(member.id, ctx.guild.id)
        if not row:
            embed = discord.Embed(
                title=member.display_name,
                description=config.AFK_CHECKED_NOT_AFK,
                color=discord.Color.green(),
            )
            await ctx.send(embed=embed)
            return

        afk_since = datetime.fromisoformat(row["afk_since"])
        duration = int((datetime.now() - afk_since).total_seconds())
        reason = row.get("afk_reason") or "Отошёл"

        embed = discord.Embed(
            title=member.display_name,
            color=discord.Color.orange(),
        )
        embed.add_field(name="Статус", value=config.AFK_AFK_STATUS, inline=False)
        embed.add_field(name="Причина", value=reason, inline=False)
        embed.add_field(name="Ушёл", value=afk_since.strftime("%H:%M"), inline=True)
        embed.add_field(name="Время в AFK", value=format_duration(duration), inline=True)

        await ctx.send(embed=embed)

    @commands.command(name="afk_stats")
    async def afk_stats_command(self, ctx: commands.Context, member: discord.Member):
        stats = get_user_stats(member.id)
        if not stats:
            embed = discord.Embed(
                title=member.display_name,
                description=config.AFK_STATS_NO_DATA,
                color=discord.Color.blue(),
            )
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(
            title=f"{config.AFK_STATS_TITLE}: {member.display_name}",
            color=discord.Color.blue(),
        )
        embed.add_field(name=config.AFK_STATS_TOTAL, value=stats["total_afk_count"], inline=True)
        embed.add_field(
            name=config.AFK_STATS_TOTAL_TIME,
            value=format_duration(stats["total_afk_seconds"]),
            inline=True,
        )
        embed.add_field(
            name=config.AFK_STATS_LONGEST,
            value=format_duration(stats["longest_afk_seconds"]),
            inline=False,
        )

        await ctx.send(embed=embed)
