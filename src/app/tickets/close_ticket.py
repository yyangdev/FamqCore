import discord


class CloseButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Закрыть тикет", style=discord.ButtonStyle.danger)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message("Тикет закрывается...")
        await interaction.channel.delete()
