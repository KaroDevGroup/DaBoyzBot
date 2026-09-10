import discord
from discord.ext import commands
import json
import os

from utils.embeds import success_embed, error_embed

GUILD_ID = 908868924488171540

WARNINGS_FILE = "warnings.json"

WARN_REMOVE_ROLE_IDS = {
    1006808943315648602,  # Staff
    1541650077624307772,  # Senior Staff
    1546298106763804832,  # Management
    908882405153202236,   # Owner
}

class WarnRemove(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def load_warnings(self):
        if not os.path.exists(WARNINGS_FILE):
            return {}

        try:
            with open(WARNINGS_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except (json.JSONDecodeError, OSError):
            return {}

    def save_warnings(self, warnings):
        with open(WARNINGS_FILE, "w", encoding="utf-8") as file:
            json.dump(warnings, file, indent=4)

    @discord.app_commands.command(
        name="warn_remove",
        description="Remove a warning from a member."
    )
    @discord.app_commands.guilds(discord.Object(id=GUILD_ID))
    async def warn_remove(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        warning_number: int
    ):
        if not any(role.id in WARN_REMOVE_ROLE_IDS for role in interaction.user.roles):
            await interaction.response.send_message(
                embed=error_embed(
                    "❌ Permission Denied",
                    "You don't have permission to use this command."
                ),
                ephemeral=True
            )
            return

        warnings = self.load_warnings()
        user_id = str(member.id)

        if user_id not in warnings or not warnings[user_id]:
            await interaction.response.send_message(
                embed=error_embed(
                    "❌ No Warnings",
                    f"**{member}** has no warnings."
                ),
                ephemeral=True
            )
            return

        user_warnings = warnings[user_id]

        warning_to_remove = next(
            (
                warning
                for warning in user_warnings
                if warning.get("id") == warning_number
            ),
            None
        )

        if warning_to_remove is None:
            await interaction.response.send_message(
                embed=error_embed(
                    "❌ Warning Not Found",
                    f"Warning **#{warning_number}** does not exist for **{member}**."
                ),
                ephemeral=True
            )
            return

        removed_reason = warning_to_remove.get(
            "reason",
            "No reason provided"
        )

        warnings[user_id].remove(warning_to_remove)

        self.save_warnings(warnings)

        await interaction.response.send_message(
            embed=success_embed(
                "🗑️ Warning Removed",
                f"**Member:** {member}\n"
                f"**Warning #:** {warning_number}\n"
                f"**Original Reason:** {removed_reason}\n"
                f"**Moderator:** {interaction.user}"
            )
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(WarnRemove(bot))