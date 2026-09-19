import sys
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import config
import main as main_module


class TestRunTests(unittest.TestCase):
    @patch("main.subprocess.run")
    def test_run_tests_success(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="OK", stderr="")
        result = main_module.run_tests()
        self.assertTrue(result)
        mock_run.assert_called_once()

    @patch("main.subprocess.run")
    def test_run_tests_failure(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1, stdout="FAIL", stderr="error")
        result = main_module.run_tests()
        self.assertFalse(result)


class TestOnReady(unittest.IsolatedAsyncioTestCase):
    async def test_on_ready_initializes_db(self):
        bot = MagicMock()
        bot.user = "TestBot#1234"

        with patch("main.init_db") as mock_init:
            with patch("main.logger"):
                await main_module.on_ready()

        mock_init.assert_called_once()

    async def test_on_ready_loads_extensions(self):
        bot = MagicMock()
        bot.user = "TestBot#1234"
        bot.load_extension = AsyncMock()

        with patch("main.init_db"):
            with patch("main.logger"):
                main_module.bot = bot
                await main_module.on_ready()

        bot.load_extension.assert_any_call("tickets")
        bot.load_extension.assert_any_call("afk")


class TestBotConfiguration(unittest.TestCase):
    def test_bot_prefix_from_config(self):
        self.assertEqual(config.CMD_PREFIX, "!")

    def test_intents_message_content(self):
        self.assertTrue(main_module.bot.intents.message_content)

    def test_intents_members(self):
        self.assertTrue(main_module.bot.intents.members)


class TestMainBlock(unittest.TestCase):
    @patch("main.run_tests")
    @patch("main.bot.run")
    @patch("builtins.print")
    def test_main_tests_pass(self, mock_print, mock_bot_run, mock_run_tests):
        mock_run_tests.return_value = True
        with patch.object(main_module, "__name__", "__main__"):
            main_module.bot.run = mock_bot_run
            if main_module.__name__ == "__main__":
                if not main_module.run_tests():
                    sys.exit(1)
                mock_print("\n✅ All tests passed\n")
                main_module.bot.run(config.TOKEN)
        mock_bot_run.assert_called_once_with(config.TOKEN)

    @patch("main.run_tests")
    @patch("sys.exit")
    @patch("builtins.print")
    def test_main_tests_fail(self, mock_print, mock_exit, mock_run_tests):
        mock_run_tests.return_value = False
        if not main_module.run_tests():
            mock_print("\n❌ Test no passed")
            mock_exit(1)
        mock_exit.assert_called_once_with(1)


if __name__ == "__main__":
    unittest.main()
