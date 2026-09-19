from datetime import datetime

import discord

import config
from database.tickets_db import get_ticket, update_ticket_status
from utils.logger import logger


class DenyButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Отказать", style=discord.ButtonStyle.danger)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(DenyReasonModal(interaction.channel))


class DenyReasonModal(discord.ui.Modal):
    def __init__(self, channel):
        super().__init__(title="Отклонение заявки")
        self.channel = channel
        self.reason = discord.ui.TextInput(
            label="Причина отказа",
            placeholder="Укажите причину",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=500,
        )
        self.add_item(self.reason)

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        log_ch = discord.utils.get(guild.channels, name=config.LOG_CHANNEL_NAME)
        if not log_ch:
            log_ch = await guild.create_text_channel(config.LOG_CHANNEL_NAME)

        ticket = get_ticket(self.channel.id)
        applicant = guild.get_member(ticket["user_id"]) if ticket else None

        update_ticket_status(self.channel.id, "denied", interaction.user.id, self.reason.value)

        embed = discord.Embed(
            title=config.DENY_EMBED_TITLE,
            color=discord.Color.red(),
            timestamp=datetime.now(),
        )
        embed.add_field(
            name="Заявитель", value=applicant.mention if applicant else "—", inline=False
        )
        embed.add_field(name="Причина", value=self.reason.value, inline=False)
        embed.add_field(name="Рекрут", value=interaction.user.mention, inline=False)
        await log_ch.send(embed=embed)

        await self.channel.send(f"❌ Заявка отклонена! Причина: {self.reason.value}")
        await interaction.response.send_message(
            "Заявка отклонена. Тикет удаляется.", ephemeral=True
        )

        logger.info(f"Тикет {self.channel.id} отклонён, удаляю канал")
        await self.channel.delete()
