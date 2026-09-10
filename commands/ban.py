# KaroDevGroup

import discord
from discord.ext import commands
from utils.embeds import success_embed, error_embed

GUILD_ID = 908868924488171540

BAN_ROLE_IDS = {
    1541650077624307772,  # Senior Staff
    1546298106763804832,  # Management
    908882405153202236,   # Owner
}

class Ban(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.app_commands.command(
        name="ban",
        description="Ban a member from the server."
    )
    @discord.app_commands.guilds(discord.Object(id=GUILD_ID))
    async def ban(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str = "No reason provided"
    ):
        if not any(role.id in BAN_ROLE_IDS for role in interaction.user.roles):
            await interaction.response.send_message(
                embed=error_embed(
                    "❌ Permission Denied",
                    "You don't have permission to use this command."
                ),
                ephemeral=True
            )
            return

        if not interaction.guild.me.guild_permissions.ban_members:
            await interaction.response.send_message(
                embed=error_embed(
                    "❌ Missing Permission",
                    "I don't have permission to ban members."
                ),
                ephemeral=True
            )
            return

        if member.id == interaction.guild.owner_id:
            await interaction.response.send_message(
                embed=error_embed(
                    "❌ Action Denied",
                    "You cannot ban the server owner."
                ),
                ephemeral=True
            )
            return

        if member.id == interaction.user.id:
            await interaction.response.send_message(
                embed=error_embed(
                    "❌ Action Denied",
                    "You cannot ban yourself."
                ),
                ephemeral=True
            )
            return

        if member.top_role >= interaction.guild.me.top_role:
            await interaction.response.send_message(
                embed=error_embed(
                    "❌ Action Denied",
                    "I cannot ban this member because their highest role "
                    "is equal to or higher than my highest role."
                ),
                ephemeral=True
            )
            return

        try:
            await member.ban(
                reason=f"{reason} | Banned by {interaction.user}"
            )

            await interaction.response.send_message(
                embed=success_embed(
                    "🔨 Member Banned",
                    f"**Member:** {member}\n"
                    f"**Reason:** {reason}\n"
                    f"**Moderator:** {interaction.user}"
                )
            )

        except discord.Forbidden:
            await interaction.response.send_message(
                embed=error_embed(
                    "❌ Ban Failed",
                    "Discord denied the ban. Check my role position and permissions."
                ),
                ephemeral=True
            )

        except discord.HTTPException as e:
            print(f"Ban error: {e}")

            await interaction.response.send_message(
                embed=error_embed(
                    "❌ Ban Failed",
                    "An error occurred while attempting to ban this member."
                ),
                ephemeral=True
            )

async def setup(bot: commands.Bot):
    await bot.add_cog(Ban(bot))