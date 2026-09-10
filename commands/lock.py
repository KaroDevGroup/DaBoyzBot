# KaroDevGroup

import discord
from discord.ext import commands
from utils.embeds import success_embed, error_embed

GUILD_ID = 908868924488171540

LOCK_ROLE_IDS = {
    1541650077624307772,  # Senior Staff
    1546298106763804832,  # Management
    908882405153202236,   # Owner
}

class Lock(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.app_commands.command(
        name="lock",
        description="Lock the current channel."
    )
    @discord.app_commands.guilds(discord.Object(id=GUILD_ID))
    async def lock(self, interaction: discord.Interaction):

        if not any(role.id in LOCK_ROLE_IDS for role in interaction.user.roles):
            await interaction.response.send_message(
                embed=error_embed(
                    "❌ Permission Denied",
                    "You don't have permission to use this command."
                ),
                ephemeral=True
            )
            return

        if not interaction.guild.me.guild_permissions.manage_channels:
            await interaction.response.send_message(
                embed=error_embed(
                    "❌ Missing Permission",
                    "I don't have permission to manage this channel."
                ),
                ephemeral=True
            )
            return

        channel = interaction.channel

        try:
            overwrite = channel.overwrites_for(
                interaction.guild.default_role
            )
            overwrite.send_messages = False

            await channel.set_permissions(
                interaction.guild.default_role,
                overwrite=overwrite,
                reason=f"Channel locked by {interaction.user}"
            )

            await interaction.response.send_message(
                embed=success_embed(
                    "🔒 Channel Locked",
                    f"**Channel:** {channel.name}\n\n"
                    "Members can no longer send messages in this channel."
                )
            )

        except discord.Forbidden:
            await interaction.response.send_message(
                embed=error_embed(
                    "❌ Lock Failed",
                    "Discord denied the channel lock. Check my permissions."
                ),
                ephemeral=True
            )

        except discord.HTTPException as e:
            print(f"Lock error: {e}")

            await interaction.response.send_message(
                embed=error_embed(
                    "❌ Lock Failed",
                    "An error occurred while attempting to lock this channel."
                ),
                ephemeral=True
            )

async def setup(bot: commands.Bot):
    await bot.add_cog(Lock(bot))