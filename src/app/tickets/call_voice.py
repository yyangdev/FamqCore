import discord

import config
from database.tickets_db import get_ticket


class VoiceCallButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Вызвать на обзвон", style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "Выберите канал:", view=VoiceSelectView(interaction.channel), ephemeral=True
        )


class VoiceSelectView(discord.ui.View):
    def __init__(self, channel):
        super().__init__(timeout=60)
        self.ticket_channel = channel
        for i, name in enumerate(config.VOICE_CHANNELS, 1):
            btn = discord.ui.Button(
                label=name, style=discord.ButtonStyle.success, custom_id=f"voice{i}"
            )
            btn.callback = self.make_callback(name)
            self.add_item(btn)

    def make_callback(self, voice_name):
        async def callback(interaction: discord.Interaction):
            ticket = get_ticket(self.ticket_channel.id)
            applicant = interaction.guild.get_member(ticket["user_id"]) if ticket else None
            recruiter = interaction.user
            voice_ch = discord.utils.get(interaction.guild.voice_channels, name=voice_name)

            if not voice_ch:
                await self.ticket_channel.send(f"❌ Канал {voice_name} не найден!")
                await interaction.response.send_message(
                    f"Канал {voice_name} не найден", ephemeral=True
                )
                return

            await self.ticket_channel.send(
                f"**Рекрут** {recruiter.mention} **вызвал** {applicant.mention if applicant else 'заявителя'} **на обзвон**"
            )
            await self.ticket_channel.send(
                f"{applicant.mention if applicant else 'Заявитель'} зайдите в {voice_ch.mention}"
            )
            await interaction.response.send_message(
                f"Вызов отправлен в {voice_ch.mention}", ephemeral=True
            )

        return callback
