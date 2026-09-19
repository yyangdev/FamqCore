import re
from datetime import datetime, timedelta

import discord

import config


def parse_return_time(text: str):
    text = text.lower().strip()
    now = datetime.now()

    # Формат ЧЧ:ММ
    try:
        dt = datetime.strptime(text, "%H:%M")
        target = now.replace(hour=dt.hour, minute=dt.minute, second=0, microsecond=0)
        if target <= now:
            target += timedelta(days=1)
        return target
    except ValueError:
        pass

    # Поиск числа и ключевых слов
    match = re.search(r"(\d+)", text)
    if not match:
        return None
    num = int(match.group(1))

    if "час" in text or "ч" in text:
        return now + timedelta(hours=num)
    elif "мин" in text or "м" in text:
        return now + timedelta(minutes=num)

    return None


async def build_afk_embed(guild: discord.Guild):
    from .models import get_all_afk

    rows = get_all_afk(guild.id)

    embed = discord.Embed(
        title=config.AFK_MENU_TITLE,
        color=discord.Color.red(),
    )
    embed.add_field(name=config.AFK_MENU_TOTAL, value=f"{len(rows)} человек", inline=False)

    lines = []
    for idx, row in enumerate(rows, 1):
        member = guild.get_member(row["user_id"])
        name = member.mention if member else f"<@{row['user_id']}>"
        reason = row.get("afk_reason") or config.AFK_REASON_DEFAULT
        afk_since = datetime.fromisoformat(row["afk_since"])
        since_str = afk_since.strftime("%H:%M")
        return_str = "—"
        if row.get("estimated_return"):
            try:
                ret = datetime.fromisoformat(row["estimated_return"])
                return_str = ret.strftime("%H:%M")
            except Exception:
                return_str = str(row["estimated_return"])[:20]
        lines.append(
            f"{idx}) {name} | Причина: {reason}    Ушел: {since_str} | Вернется: {return_str}"
        )

    if lines:
        embed.description = "\n".join(lines)
    else:
        embed.description = config.AFK_MENU_NO_AFK

    return embed


class AfkReturnView(discord.ui.View):
    def __init__(self, member: discord.Member, guild_id: int, duration_text: str):
        super().__init__(timeout=60)
        self.member = member
        self.guild_id = guild_id
        self.duration_text = duration_text

    @discord.ui.button(label=config.AFK_BUTTON_RETURN, style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.member.id:
            await interaction.response.send_message(config.AFK_INVALID_USER, ephemeral=True)
            return

        from .models import remove_afk, remove_afk_nickname

        duration = remove_afk(self.member.id, self.guild_id)
        if duration is None:
            await interaction.response.send_message(config.AFK_RETURN_ERROR, ephemeral=True)
            return

        await remove_afk_nickname(self.member)
        await interaction.response.edit_message(
            content=f"{config.AFK_RETURN_SUCCESS} Отсутствовали: {self.duration_text}.",
            embed=None,
            view=None,
        )
        self.stop()

    @discord.ui.button(label=config.AFK_BUTTON_STAY, style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.member.id:
            await interaction.response.send_message(config.AFK_INVALID_USER, ephemeral=True)
            return
        await interaction.response.edit_message(
            content=config.AFK_RETURN_STAY, embed=None, view=None
        )
        self.stop()


class AfkSetModal(discord.ui.Modal, title=config.AFK_MODAL_TITLE):
    reason = discord.ui.TextInput(
        label=config.AFK_MODAL_REASON_LABEL,
        placeholder=config.AFK_MODAL_REASON_PLACEHOLDER,
        required=False,
        max_length=100,
    )
    duration = discord.ui.TextInput(
        label=config.AFK_MODAL_DURATION_LABEL,
        placeholder=config.AFK_MODAL_DURATION_PLACEHOLDER,
        required=True,
        max_length=50,
    )

    def __init__(self, member: discord.Member, guild_id: int, guild: discord.Guild):
        super().__init__()
        self.member = member
        self.guild_id = guild_id
        self.guild = guild

    async def on_submit(self, interaction: discord.Interaction):
        from .models import add_afk_nickname, set_afk

        reason = self.reason.value or config.AFK_REASON_DEFAULT
        parsed = parse_return_time(self.duration.value)
        if parsed is None:
            await interaction.response.send_message(
                "❌ Не удалось распознать время. Попробуйте снова.",
                ephemeral=True,
            )
            return

        estimated_return = parsed.isoformat()
        set_afk(self.member.id, self.guild_id, reason, estimated_return)
        await add_afk_nickname(self.member)
        await interaction.response.send_message(
            f"🔴 Вы в AFK.\nПричина: {reason}\nВернётесь: <t:{int(parsed.timestamp())}:R>",
            ephemeral=True,
        )


class AfkMenuView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label=config.AFK_BUTTON_LEAVE, style=discord.ButtonStyle.danger)
    async def leave(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = AfkSetModal(interaction.user, interaction.guild_id, interaction.guild)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label=config.AFK_BUTTON_RETURN, style=discord.ButtonStyle.success)
    async def return_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        from .models import get_afk_user

        row = get_afk_user(interaction.user.id, interaction.guild_id)
        if not row:
            await interaction.response.send_message(config.AFK_NOT_AFK, ephemeral=True)
            return

        afk_since = datetime.fromisoformat(row["afk_since"])
        duration = datetime.now() - afk_since
        hours, remainder = divmod(int(duration.total_seconds()), 3600)
        minutes, _ = divmod(remainder, 60)
        duration_text = f"{hours} часов {minutes} минут" if hours else f"{minutes} минут"

        embed = discord.Embed(
            title=config.AFK_RETURN_MODAL_TITLE,
            description=f"{config.AFK_RETURN_CONFIRM}\n\n**{config.AFK_RETURN_DURATION_LABEL}:** {duration_text}",
            color=discord.Color.orange(),
        )
        view = AfkReturnView(interaction.user, interaction.guild_id, duration_text)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(label=config.AFK_BUTTON_REFRESH, style=discord.ButtonStyle.primary)
    async def refresh(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = await build_afk_embed(interaction.guild)
        await interaction.response.send_message(embed=embed, ephemeral=True)
