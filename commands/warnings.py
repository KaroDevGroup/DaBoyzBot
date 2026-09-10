# KaroDevGroup

import discord
from discord.ext import commands
import json
import os
from datetime import datetime

from utils.embeds import success_embed, error_embed

GUILD_ID = 908868924488171540

WARNINGS_FILE = "warnings.json"

WARNINGS_ROLE_IDS = {
    1488309396797653112,  # Trial Staff
    1006808943315648602,  # Staff
    1541650077624307772,  # Senior Staff
    1546298106763804832,  # Management
    908882405153202236,   # Owner
}

class Warnings(commands.Cog):
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

    @discord.app_commands.command(
        name="warnings",
        description="View a member's warnings."
    )
    @discord.app_commands.guilds(discord.Object(id=GUILD_ID))
    async def warnings(
        self,
        interaction: discord.Interaction,
        member: discord.Member
    ):
        if not any(role.id in WARNINGS_ROLE_IDS for role in interaction.user.roles):
            await interaction.response.send_message(
                embed=error_embed(
                    "❌ Permission Denied",
                    "You don't have permission to use this command."
                ),
                ephemeral=True
            )
            return

        warnings = self.load_warnings()
        user_warnings = warnings.get(str(member.id), [])

        if not user_warnings:
            await interaction.response.send_message(
                embed=success_embed(
                    "✅ No Warnings",
                    f"**{member}** has no warnings."
                ),
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title=f"⚠️ Warnings for {member}",
            description=f"**Total Warnings:** {len(user_warnings)}",
            color=discord.Color.from_rgb(255, 165, 0)
        )

        for warning in user_warnings:
            try:
                warning_date = datetime.fromisoformat(
                    warning["timestamp"]
                ).strftime("%B %d, %Y")
            except (KeyError, ValueError):
                warning_date = "Unknown date"

            embed.add_field(
                name=f"Warning #{warning['id']}",
                value=(
                    f"**Reason:** {warning['reason']}\n"
                    f"**Moderator:** {warning['moderator_name']}\n"
                    f"**Date:** {warning_date}"
                ),
                inline=False
            )

        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Warnings(bot))