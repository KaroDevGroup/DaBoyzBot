# KaroDevGroup

import discord
from discord.ext import commands

from utils.embeds import success_embed, error_embed

GUILD_ID = 908868924488171540

UNBAN_ROLE_IDS = {
    1546298106763804832,  # Management
    908882405153202236,   # Owner
}

class Unban(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.app_commands.command(
        name="unban",
        description="Unban a user from the server."
    )
    @discord.app_commands.guilds(discord.Object(id=GUILD_ID))
    async def unban(
        self,
        interaction: discord.Interaction,
        user_id: str,
        reason: str = "No reason provided"
    ):
        if not any(role.id in UNBAN_ROLE_IDS for role in interaction.user.roles):
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
                    "I don't have permission to unban members."
                ),
                ephemeral=True
            )
            return

        try:
            user_id = int(user_id)
        except ValueError:
            await interaction.response.send_message(
                embed=error_embed(
                    "❌ Invalid User ID",
                    "Please provide a valid Discord User ID."
                ),
                ephemeral=True
            )
            return

        try:
            user = await self.bot.fetch_user(user_id)
        except discord.NotFound:
            await interaction.response.send_message(
                embed=error_embed(
                    "❌ User Not Found",
                    "I couldn't find a Discord user with that ID."
                ),
                ephemeral=True
            )
            return

        except discord.HTTPException:
            await interaction.response.send_message(
                embed=error_embed(
                    "❌ Request Failed",
                    "I couldn't retrieve that user from Discord."
                ),
                ephemeral=True
            )
            return

        try:
            await interaction.guild.fetch_ban(user)

        except discord.NotFound:
            await interaction.response.send_message(
                embed=error_embed(
                    "❌ User Not Banned",
                    f"**{user}** is not currently banned."
                ),
                ephemeral=True
            )
            return

        except discord.HTTPException:
            await interaction.response.send_message(
                embed=error_embed(
                    "❌ Request Failed",
                    "I couldn't check the server's ban list."
                ),
                ephemeral=True
            )
            return

        try:
            await interaction.guild.unban(
                user,
                reason=f"{reason} | Unbanned by {interaction.user}"
            )

            await interaction.response.send_message(
                embed=success_embed(
                    "🔓 Member Unbanned",
                    f"**User:** {user}\n"
                    f"**Reason:** {reason}\n"
                    f"**Moderator:** {interaction.user}"
                )
            )

        except discord.Forbidden:
            await interaction.response.send_message(
                embed=error_embed(
                    "❌ Unban Failed",
                    "Discord denied the unban. Check my permissions."
                ),
                ephemeral=True
            )

        except discord.HTTPException as e:
            print(f"Unban error: {e}")

            await interaction.response.send_message(
                embed=error_embed(
                    "❌ Unban Failed",
                    "An error occurred while attempting to unban this user."
                ),
                ephemeral=True
            )

async def setup(bot: commands.Bot):
    await bot.add_cog(Unban(bot))