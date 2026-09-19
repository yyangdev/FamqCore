import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from afk.events import setup_afk_events


class TestAfkEvents(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.bot = MagicMock()
        self.bot.process_commands = AsyncMock()
        setup_afk_events(self.bot)
        self.on_message = self.bot.event.call_args_list[0][0][0]
        self.on_voice = self.bot.event.call_args_list[1][0][0]

    def tearDown(self):
        self.loop.close()

    def test_events_registered(self):
        self.assertEqual(self.bot.event.call_count, 2)


class TestOnMessageEvent(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.bot = MagicMock()
        self.bot.process_commands = AsyncMock()
        setup_afk_events(self.bot)
        self.on_message = self.bot.event.call_args_list[0][0][0]

    def tearDown(self):
        self.loop.close()

    def test_bot_message_ignored(self):
        message = MagicMock()
        message.author.bot = True
        self.loop.run_until_complete(self.on_message(message))
        self.bot.process_commands.assert_not_called()

    def test_no_guild_ignored(self):
        message = MagicMock()
        message.author.bot = False
        message.guild = None
        self.loop.run_until_complete(self.on_message(message))
        # When guild is None, the function returns early without calling process_commands
        self.bot.process_commands.assert_not_called()

    def test_no_mentions(self):
        message = MagicMock()
        message.author.bot = False
        message.guild = MagicMock()
        message.guild.id = 123
        message.mentions = []

        self.loop.run_until_complete(self.on_message(message))
        self.bot.process_commands.assert_called_once()

    def test_mention_not_afk(self):
        message = MagicMock()
        message.author.bot = False
        message.guild = MagicMock()
        message.guild.id = 123
        message.author.id = 100
        message.mentions = [MagicMock()]
        message.mentions[0].id = 200
        message.channel = MagicMock()
        message.channel.send = AsyncMock()

        with patch("afk.events.get_afk_user") as mock_get:
            mock_get.return_value = None
            self.loop.run_until_complete(self.on_message(message))

        message.channel.send.assert_not_called()

    def test_mention_afk_with_reply(self):
        message = MagicMock()
        message.author.bot = False
        message.guild = MagicMock()
        message.guild.id = 123
        message.author.id = 100
        mention = MagicMock()
        mention.id = 200
        mention.mention = "<@200>"
        message.mentions = [mention]
        message.channel = MagicMock()
        message.channel.send = AsyncMock()

        mock_row = {"afk_since": "2024-01-01T10:00:00", "afk_reason": "test"}

        with patch("afk.events.get_afk_user") as mock_get:
            with patch("afk.events.check_and_reply") as mock_check:
                mock_get.return_value = mock_row
                mock_check.return_value = True
                self.loop.run_until_complete(self.on_message(message))

        message.channel.send.assert_called_once()

    def test_mention_afk_cooldown(self):
        message = MagicMock()
        message.author.bot = False
        message.guild = MagicMock()
        message.guild.id = 123
        message.author.id = 100
        mention = MagicMock()
        mention.id = 200
        message.mentions = [mention]
        message.channel = MagicMock()
        message.channel.send = AsyncMock()

        mock_row = {"afk_since": "2024-01-01T10:00:00", "afk_reason": "test"}

        with patch("afk.events.get_afk_user") as mock_get:
            with patch("afk.events.check_and_reply") as mock_check:
                mock_get.return_value = mock_row
                mock_check.return_value = False
                self.loop.run_until_complete(self.on_message(message))

        message.channel.send.assert_not_called()

    def test_multiple_mentions(self):
        message = MagicMock()
        message.author.bot = False
        message.guild = MagicMock()
        message.guild.id = 123
        message.author.id = 100
        mention1 = MagicMock()
        mention1.id = 200
        mention2 = MagicMock()
        mention2.id = 300
        message.mentions = [mention1, mention2]
        message.channel = MagicMock()
        message.channel.send = AsyncMock()

        mock_row = {"afk_since": "2024-01-01T10:00:00", "afk_reason": "test"}

        with patch("afk.events.get_afk_user") as mock_get:
            with patch("afk.events.check_and_reply") as mock_check:
                mock_get.return_value = mock_row
                mock_check.return_value = True
                self.loop.run_until_complete(self.on_message(message))

        self.assertEqual(message.channel.send.call_count, 2)


class TestOnVoiceStateUpdate(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.bot = MagicMock()
        self.bot.process_commands = AsyncMock()
        setup_afk_events(self.bot)
        self.on_voice = self.bot.event.call_args_list[1][0][0]

    def tearDown(self):
        self.loop.close()

    def test_join_voice_not_afk(self):
        member = MagicMock()
        member.id = 456
        member.guild = MagicMock()
        member.guild.id = 123
        member.guild.system_channel = None
        member.guild.text_channels = []

        before = MagicMock()
        before.channel = None
        after = MagicMock()
        after.channel = MagicMock()

        with patch("afk.events.get_afk_user") as mock_get:
            mock_get.return_value = None
            self.loop.run_until_complete(self.on_voice(member, before, after))

    def test_join_voice_is_afk(self):
        member = MagicMock()
        member.id = 456
        member.display_name = "TestUser"
        member.guild = MagicMock()
        member.guild.id = 123
        channel = MagicMock()
        channel.send = AsyncMock()
        member.guild.system_channel = channel
        member.guild.text_channels = []

        before = MagicMock()
        before.channel = None
        after = MagicMock()
        after.channel = MagicMock()

        with patch("afk.events.get_afk_user") as mock_get:
            with patch("afk.events.remove_afk") as mock_remove:
                with patch("afk.events.remove_afk_nickname") as mock_nick:
                    mock_get.return_value = {"afk_since": "2024-01-01T10:00:00"}
                    self.loop.run_until_complete(self.on_voice(member, before, after))

        channel.send.assert_called_once()
        mock_remove.assert_called_once()
        mock_nick.assert_called_once()

    def test_leave_voice_ignored(self):
        member = MagicMock()
        member.id = 456
        member.guild = MagicMock()
        member.guild.id = 123

        before = MagicMock()
        before.channel = MagicMock()
        after = MagicMock()
        after.channel = None

        with patch("afk.events.get_afk_user") as mock_get:
            mock_get.return_value = None
            self.loop.run_until_complete(self.on_voice(member, before, after))

    def test_move_voice_ignored(self):
        member = MagicMock()
        member.id = 456
        member.guild = MagicMock()
        member.guild.id = 123

        before = MagicMock()
        before.channel = MagicMock()
        after = MagicMock()
        after.channel = MagicMock()

        with patch("afk.events.get_afk_user") as mock_get:
            mock_get.return_value = None
            self.loop.run_until_complete(self.on_voice(member, before, after))

    def test_no_system_channel_uses_first_text(self):
        member = MagicMock()
        member.id = 456
        member.display_name = "TestUser"
        member.guild = MagicMock()
        member.guild.id = 123
        member.guild.system_channel = None
        channel = MagicMock()
        channel.send = AsyncMock()
        member.guild.text_channels = [channel]

        before = MagicMock()
        before.channel = None
        after = MagicMock()
        after.channel = MagicMock()

        with patch("afk.events.get_afk_user") as mock_get:
            with patch("afk.events.remove_afk"):
                with patch("afk.events.remove_afk_nickname"):
                    mock_get.return_value = {"afk_since": "2024-01-01T10:00:00"}
                    self.loop.run_until_complete(self.on_voice(member, before, after))

        channel.send.assert_called_once()

    def test_no_channels(self):
        member = MagicMock()
        member.id = 456
        member.display_name = "TestUser"
        member.guild = MagicMock()
        member.guild.id = 123
        member.guild.system_channel = None
        member.guild.text_channels = []

        before = MagicMock()
        before.channel = None
        after = MagicMock()
        after.channel = MagicMock()

        with patch("afk.events.get_afk_user") as mock_get:
            with patch("afk.events.remove_afk") as mock_remove:
                with patch("afk.events.remove_afk_nickname") as mock_nick:
                    mock_get.return_value = {"afk_since": "2024-01-01T10:00:00"}
                    self.loop.run_until_complete(self.on_voice(member, before, after))

        mock_remove.assert_called_once()
        mock_nick.assert_called_once()


if __name__ == "__main__":
    unittest.main()
