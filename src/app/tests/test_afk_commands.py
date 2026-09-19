import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import discord

from afk.commands import AfkCog
from afk.models import format_duration


class TestFormatDuration(unittest.TestCase):
    def test_zero_seconds(self):
        result = format_duration(0)
        self.assertEqual(result, "0 сек")

    def test_seconds_only(self):
        result = format_duration(45)
        self.assertEqual(result, "45 сек")

    def test_minutes_only(self):
        result = format_duration(120)
        self.assertEqual(result, "2 мин")

    def test_hours_only(self):
        result = format_duration(7200)
        self.assertEqual(result, "2 ч")

    def test_hours_and_minutes(self):
        result = format_duration(7500)
        self.assertEqual(result, "2 ч 5 мин")

    def test_full_duration(self):
        result = format_duration(3661)
        self.assertEqual(result, "1 ч 1 мин 1 сек")

    def test_large_duration(self):
        result = format_duration(90061)
        self.assertEqual(result, "1 дн 1 ч 1 мин 1 сек")


class TestAfkCog(unittest.TestCase):
    def setUp(self):
        self.bot = MagicMock()
        self.cog = AfkCog(self.bot)

    def test_cog_name(self):
        self.assertEqual(self.cog.qualified_name, "AfkCog")

    def test_afk_command_exists(self):
        self.assertTrue(hasattr(self.cog, "afk_command"))

    def test_afk_list_command_exists(self):
        self.assertTrue(hasattr(self.cog, "afk_list_command"))

    def test_afk_check_command_exists(self):
        self.assertTrue(hasattr(self.cog, "afk_check_command"))

    def test_afk_stats_command_exists(self):
        self.assertTrue(hasattr(self.cog, "afk_stats_command"))


class TestAfkCommand(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.bot = MagicMock()
        self.cog = AfkCog(self.bot)

    def tearDown(self):
        self.loop.close()

    def test_afk_sends_embed(self):
        ctx = MagicMock()
        ctx.send = AsyncMock()

        self.loop.run_until_complete(self.cog.afk_command.callback(self.cog, ctx))

        ctx.send.assert_called_once()
        call_args = ctx.send.call_args
        embed = call_args.kwargs.get("embed") or call_args.args[0]
        self.assertIsInstance(embed, discord.Embed)
        self.assertIn("AFK", embed.title)


class TestAfkListCommand(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.bot = MagicMock()
        self.cog = AfkCog(self.bot)

    def tearDown(self):
        self.loop.close()

    def test_afk_list_empty(self):
        ctx = MagicMock()
        ctx.send = AsyncMock()
        ctx.guild = MagicMock()
        ctx.guild.id = 123

        with patch("afk.models.get_all_afk") as mock_get:
            mock_get.return_value = []
            self.loop.run_until_complete(self.cog.afk_list_command.callback(self.cog, ctx))

        ctx.send.assert_called_once()
        call_args = ctx.send.call_args
        embed = call_args.kwargs.get("embed") or call_args.args[0]
        self.assertIn("никого нет", embed.description.lower())

    def test_afk_list_with_users(self):
        ctx = MagicMock()
        ctx.send = AsyncMock()
        ctx.guild = MagicMock()
        ctx.guild.id = 123
        ctx.guild.get_member = MagicMock(return_value=None)

        mock_rows = [
            {
                "user_id": 111,
                "afk_reason": "test",
                "afk_since": "2024-01-01T10:00:00",
                "estimated_return": None,
            },
        ]

        with patch("afk.models.get_all_afk") as mock_get:
            mock_get.return_value = mock_rows
            self.loop.run_until_complete(self.cog.afk_list_command.callback(self.cog, ctx))

        ctx.send.assert_called_once()
        call_args = ctx.send.call_args
        embed = call_args.kwargs.get("embed") or call_args.args[0]
        self.assertEqual(embed.fields[0].value, "1 человек")
        self.assertIn("<@111>", embed.description)


class TestAfkCheckCommand(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.bot = MagicMock()
        self.cog = AfkCog(self.bot)

    def tearDown(self):
        self.loop.close()

    def test_afk_check_not_afk(self):
        ctx = MagicMock()
        ctx.send = AsyncMock()
        ctx.guild = MagicMock()
        ctx.guild.id = 123

        member = MagicMock()
        member.id = 456
        member.display_name = "TestUser"

        with patch("afk.commands.get_afk_user") as mock_get:
            mock_get.return_value = None
            self.loop.run_until_complete(self.cog.afk_check_command.callback(self.cog, ctx, member))

        ctx.send.assert_called_once()
        call_args = ctx.send.call_args
        embed = call_args.kwargs.get("embed") or call_args.args[0]
        self.assertIn("не в AFK", embed.description)

    def test_afk_check_user_is_afk(self):
        ctx = MagicMock()
        ctx.send = AsyncMock()
        ctx.guild = MagicMock()
        ctx.guild.id = 123

        member = MagicMock()
        member.id = 456
        member.display_name = "TestUser"

        mock_row = {
            "afk_since": "2024-01-01T10:00:00",
            "afk_reason": "test reason",
        }

        with patch("afk.commands.get_afk_user") as mock_get:
            mock_get.return_value = mock_row
            self.loop.run_until_complete(self.cog.afk_check_command.callback(self.cog, ctx, member))

        ctx.send.assert_called_once()
        call_args = ctx.send.call_args
        embed = call_args.kwargs.get("embed") or call_args.args[0]
        self.assertIn("В АФК", embed.fields[0].value)


class TestAfkStatsCommand(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.bot = MagicMock()
        self.cog = AfkCog(self.bot)

    def tearDown(self):
        self.loop.close()

    def test_afk_stats_no_data(self):
        ctx = MagicMock()
        ctx.send = AsyncMock()

        member = MagicMock()
        member.id = 456
        member.display_name = "TestUser"

        with patch("afk.commands.get_user_stats") as mock_get:
            mock_get.return_value = None
            self.loop.run_until_complete(self.cog.afk_stats_command.callback(self.cog, ctx, member))

        ctx.send.assert_called_once()
        call_args = ctx.send.call_args
        embed = call_args.kwargs.get("embed") or call_args.args[0]
        self.assertIn("TestUser", embed.title)

    def test_afk_stats_with_data(self):
        ctx = MagicMock()
        ctx.send = AsyncMock()

        member = MagicMock()
        member.id = 456
        member.display_name = "TestUser"

        mock_stats = {
            "total_afk_count": 5,
            "total_afk_seconds": 3600,
            "longest_afk_seconds": 1800,
        }

        with patch("afk.commands.get_user_stats") as mock_get:
            mock_get.return_value = mock_stats
            self.loop.run_until_complete(self.cog.afk_stats_command.callback(self.cog, ctx, member))

        ctx.send.assert_called_once()
        call_args = ctx.send.call_args
        embed = call_args.kwargs.get("embed") or call_args.args[0]
        self.assertIn("Статистика", embed.title)


if __name__ == "__main__":
    unittest.main()
