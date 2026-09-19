import discord

from .accept_ticket import AcceptButton
from .call_voice import VoiceCallButton
from .close_ticket import CloseButton
from .deny_ticket import DenyButton


class FullTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(AcceptButton())
        self.add_item(DenyButton())
        self.add_item(VoiceCallButton())
        self.add_item(CloseButton())
