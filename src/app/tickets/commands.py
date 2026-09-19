import discord
from discord.ext import commands

import config
from database.tickets_db import get_all_tickets, get_stats

from .create_ticket import TicketModal


class TicketTypeView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        rp = discord.ui.Button(
            label=config.TICKET_RP_TITLE, style=discord.ButtonStyle.success, custom_id="rp"
        )
        rp.callback = self.rp_callback
        self.add_item(rp)

        capt = discord.ui.Button(
            label=config.TICKET_CAPT_TITLE, style=discord.ButtonStyle.primary, custom_id="capt"
        )
        capt.callback = self.capt_callback
        self.add_item(capt)

    async def rp_callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(
            TicketModal(config.TICKET_RP_TITLE, "rp", config.RP_FIELDS)
        )

    async def capt_callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(
            TicketModal(config.TICKET_CAPT_TITLE, "capt", config.CAPT_FIELDS)
        )


class TicketsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name=config.CMD_REGENT)
    async def regent_apply(self, ctx):
        embed = discord.Embed(
            title=config.REGENT_EMBED_TITLE,
            description=config.REGENT_EMBED_DESCRIPTION,
            color=discord.Color.blue(),
        )
        await ctx.send(embed=embed, view=TicketTypeView())

    @commands.command(name=config.CMD_STATS)
    @commands.has_permissions(administrator=True)
    async def show_stats(self, ctx):
        stats = get_stats()
        embed = discord.Embed(title="Статистика заявок", color=discord.Color.gold())
        embed.add_field(name="Всего", value=stats["total"], inline=True)
        embed.add_field(name="Принято", value=stats["accepted"], inline=True)
        embed.add_field(name="Отклонено", value=stats["denied"], inline=True)
        embed.add_field(name="Открыто", value=stats["open"], inline=True)
        await ctx.send(embed=embed)

    @commands.command(name=config.CMD_HISTORY)
    @commands.has_permissions(administrator=True)
    async def show_history(self, ctx, limit: int = 10):
        tickets = get_all_tickets(limit)
        if not tickets:
            await ctx.send("Нет заявок в истории")
            return

        embed = discord.Embed(title="История заявок", color=discord.Color.blue())
        for t in tickets:
            emoji = "✅" if t["status"] == "accepted" else "❌" if t["status"] == "denied" else "🟡"
            embed.add_field(
                name=f"{emoji} {t['topic']}",
                value=f"От: <@{t['user_id']}>\n{t['created_at'][:10]}",
                inline=False,
            )
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(TicketsCog(bot))
