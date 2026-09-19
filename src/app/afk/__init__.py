from .commands import AfkCog
from .events import setup_afk_events


async def setup(bot):
    await bot.add_cog(AfkCog(bot))
    setup_afk_events(bot)
