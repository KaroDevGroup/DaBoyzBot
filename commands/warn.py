# KaroDevGroup

import discord
from discord.ext import commands
import json
import os
from datetime import datetime, timezone
from utils.embeds import success_embed, error_embed

GUILD_ID = 908868924488171540

WARN_ROLE_IDS = {
    1488309396797653112,  # Trial Staff
    1006808943315648602,  # Staff
    1541650077624307772,  # Senior Staff
    1546298106763804832,  # Management
    908882405153202236,   # Owner
}

WARNINGS_FILE = "warnings.json"

class Warn(commands.Cog):
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
        name="warn",
        description="Warn a member."
    )
    @discord.app_commands.guilds(discord.Object(id=GUILD_ID))
    async def warn(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str = "No reason provided"
    ):
        if not any(role.id in WARN_ROLE_IDS for role in interaction.user.roles):
            await interaction.response.send_message(
                embed=error_embed(
                    "❌ Permission Denied",
                    "You don't have permission to use this command."
                ),
                ephemeral=True
            )
            return

        if member.id == interaction.guild.owner_id:
            await interaction.response.send_message(
                embed=error_embed(
                    "❌ Action Denied",
                    "You cannot warn the server owner."
                ),
                ephemeral=True
            )
            return

        if member.id == interaction.user.id:
            await interaction.response.send_message(
                embed=error_embed(
                    "❌ Action Denied",
                    "You cannot warn yourself."
                ),
                ephemeral=True
            )
            return

        if member.top_role >= interaction.guild.me.top_role:
            await interaction.response.send_message(
                embed=error_embed(
                    "❌ Action Denied",
                    "I cannot warn this member because their highest role "
                    "is equal to or higher than my highest role."
                ),
                ephemeral=True
            )
            return

        warnings = self.load_warnings()

        user_id = str(member.id)

        if user_id not in warnings:
            warnings[user_id] = []

        warning_number = len(warnings[user_id]) + 1

        warnings[user_id].append({
            "id": warning_number,
            "reason": reason,
            "moderator": interaction.user.id,
            "moderator_name": str(interaction.user),
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

        self.save_warnings(warnings)

        await interaction.response.send_message(
            embed=success_embed(
                "⚠️ Member Warned",
                f"**Member:** {member}\n"
                f"**Warning #:** {warning_number}\n"
                f"**Reason:** {reason}\n"
                f"**Moderator:** {interaction.user}"
            )
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(Warn(bot))