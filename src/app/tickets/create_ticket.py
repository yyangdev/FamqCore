import json
from datetime import datetime

import discord

import config
from database.tickets_db import save_ticket
from utils.logger import logger

from .views import FullTicketView


class TicketModal(discord.ui.Modal):
    def __init__(self, title, ticket_type, fields):
        super().__init__(title=title)
        self.ticket_type = ticket_type
        self.inputs = {}

        for label, placeholder, required, max_length in fields:
            style = discord.TextStyle.paragraph if max_length > 150 else discord.TextStyle.short
            inp = discord.ui.TextInput(
                label=label,
                placeholder=placeholder,
                style=style,
                required=required,
                max_length=max_length,
            )
            self.inputs[label] = inp
            self.add_item(inp)

    async def on_submit(self, interaction: discord.Interaction):
        logger.info(f"Пользователь {interaction.user} подал {self.ticket_type} заявку")
        await create_ticket(interaction, self.title, self.ticket_type, self.inputs)


async def create_ticket(interaction, topic, ticket_type, inputs):
    guild = interaction.guild
    member = interaction.user

    try:
        await interaction.response.send_message("Создаю заявку...", ephemeral=True)
    except discord.InteractionResponded:
        pass

    try:
        apply_role = discord.utils.get(guild.roles, name=config.ROLE_APPLIED)
        if apply_role and apply_role < guild.me.top_role:
            try:
                await member.add_roles(apply_role)
            except discord.Forbidden:
                logger.warning(f"Нет прав на выдачу роли {apply_role.name}")

        try:
            dm = await member.create_dm()
            await dm.send(config.DM_MESSAGE)
        except discord.Forbidden:
            pass

        category = discord.utils.get(guild.categories, name=config.TICKETS_CATEGORY_NAME)
        if not category:
            category = await guild.create_category(config.TICKETS_CATEGORY_NAME)

        answers = {label: inp.value for label, inp in inputs.items()}
        channel_name = f"{ticket_type}-{member.name}".lower()

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            member: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        }

        for role_name in [
            config.ROLE_RECRUITER,
            config.ROLE_OWNER,
            config.ROLE_DEP_OWNER,
            config.ROLE_ADMIN,
            config.ROLE_SUPPORT,
        ]:
            role = discord.utils.get(guild.roles, name=role_name)
            if role:
                overwrites[role] = discord.PermissionOverwrite(
                    read_messages=True, send_messages=True
                )

        channel = await guild.create_text_channel(
            channel_name, category=category, overwrites=overwrites
        )

        save_ticket(
            channel.id,
            member.id,
            member.name,
            topic,
            ticket_type,
            json.dumps(answers, ensure_ascii=False),
            datetime.now().isoformat(),
        )

        embed = discord.Embed(title=topic, color=discord.Color.gold(), timestamp=datetime.now())
        embed.add_field(name="От кого", value=member.mention, inline=False)
        for label, value in answers.items():
            embed.add_field(name=label, value=value or "—", inline=False)

        role_mentions = []
        for role_name in [config.ROLE_RECRUITER, config.ROLE_OWNER, config.ROLE_DEP_OWNER]:
            role = discord.utils.get(guild.roles, name=role_name)
            if role:
                role_mentions.append(role.mention)

        await channel.send(embed=embed, view=FullTicketView())
        if role_mentions:
            await channel.send(f"{member.mention} {' '.join(role_mentions)}")

        await interaction.edit_original_response(content=f"Заявка создана! {channel.mention}")
        logger.info(f"Заявка {ticket_type} создана для {member.name} в {channel.name}")

    except Exception as e:
        logger.error(f"Ошибка создания заявки: {e}")
        await interaction.edit_original_response(content=config.ERROR_TICKET_CREATE)
