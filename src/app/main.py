import subprocess
import sys

import discord
from discord.ext import commands

import config
from database.tickets_db import init_db
from utils.logger import logger


def run_tests():
    result = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    return result.returncode == 0


intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=config.CMD_PREFIX, intents=intents)


@bot.event
async def on_ready():
    init_db()
    await bot.load_extension("tickets")
    await bot.load_extension("afk")
    logger.info(f"Бот {bot.user} запущен")


if __name__ == "__main__":
    if not run_tests():
        print("\n❌ Test no passed")
        sys.exit(1)
    print("\n✅ All tests passed\n")
    bot.run(config.TOKEN)
