from dataclasses import dataclass
from datetime import datetime

import discord

import config
from database.tickets_db import get_ticket, update_ticket_status
from utils.logger import logger


@dataclass(frozen=True)
class Decision:
    status: str
    modal_title: str
    reason_label: str
    embed_title: str
    embed_color: discord.Color
    channel_note: str
    reply_text: str
    log_text: str


ACCEPT = Decision(
    status="accepted",
    modal_title="Принятие заявки",
    reason_label="Причина принятия",
    embed_title=config.ACCEPT_EMBED_TITLE,
    embed_color=discord.Color.green(),
    channel_note="✅ Заявка принята! {mention}",
    reply_text="Заявка принята",
    log_text="принят",
)

DENY = Decision(
    status="denied",
    modal_title="Отклонение заявки",
    reason_label="Причина отказа",
    embed_title=config.DENY_EMBED_TITLE,
    embed_color=discord.Color.red(),
    channel_note="❌ Заявка отклонена! Причина: {reason}",
    reply_text="Заявка отклонена",
    log_text="отклонён",
)


class DecisionReasonModal(discord.ui.Modal):
    def __init__(self, channel, decision):
        super().__init__(title=decision.modal_title)
        self.channel = channel
        self.decision = decision
        self.reason = discord.ui.TextInput(
            label=decision.reason_label,
            placeholder="Укажите причину",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=500,
        )
        self.add_item(self.reason)

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        decision = self.decision

        log_ch = discord.utils.get(guild.channels, name=config.LOG_CHANNEL_NAME)
        if not log_ch:
            log_ch = await guild.create_text_channel(config.LOG_CHANNEL_NAME)

        ticket = get_ticket(self.channel.id)
        applicant = guild.get_member(ticket["user_id"]) if ticket else None
        mention = applicant.mention if applicant else "—"

        update_ticket_status(
            self.channel.id, decision.status, interaction.user.id, self.reason.value
        )

        embed = discord.Embed(
            title=decision.embed_title,
            color=decision.embed_color,
            timestamp=datetime.now(),
        )
        embed.add_field(name="Заявитель", value=mention, inline=False)
        embed.add_field(name="Причина", value=self.reason.value, inline=False)
        embed.add_field(name="Рекрут", value=interaction.user.mention, inline=False)
        await log_ch.send(embed=embed)

        await self.channel.send(
            decision.channel_note.format(mention=mention, reason=self.reason.value)
        )
        await interaction.response.send_message(
            f"{decision.reply_text}. Тикет удаляется.", ephemeral=True
        )

        logger.info(f"Тикет {self.channel.id} {decision.log_text}, удаляю канал")
        await self.channel.delete()


class DecisionButton(discord.ui.Button):
    decision = None

    async def callback(self, interaction: discord.Interaction):
        modal = DecisionReasonModal(interaction.channel, self.decision)
        await interaction.response.send_modal(modal)


class AcceptButton(DecisionButton):
    decision = ACCEPT

    def __init__(self):
        super().__init__(label="Принять", style=discord.ButtonStyle.success)


class DenyButton(DecisionButton):
    decision = DENY

    def __init__(self):
        super().__init__(label="Отказать", style=discord.ButtonStyle.danger)
