# KaroDevGroup

import discord
from discord.ext import commands
from utils.embeds import success_embed, error_embed

GUILD_ID = 908868924488171540

UNLOCK_ROLE_IDS = {
    1541650077624307772,  # Senior Staff
    1546298106763804832,  # Management
    908882405153202236,   # Owner
}

class Unlock(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.app_commands.command(
        name="unlock",
        description="Unlock the current channel."
    )
    @discord.app_commands.guilds(discord.Object(id=GUILD_ID))
    async def unlock(self, interaction: discord.Interaction):

        if not any(role.id in UNLOCK_ROLE_IDS for role in interaction.user.roles):
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
            overwrite.send_messages = None

            await channel.set_permissions(
                interaction.guild.default_role,
                overwrite=overwrite,
                reason=f"Channel unlocked by {interaction.user}"
            )

            await interaction.response.send_message(
                embed=success_embed(
                    "🔓 Channel Unlocked",
                    f"**Channel:** {channel.name}\n\n"
                    "Members can now send messages in this channel."
                )
            )

        except discord.Forbidden:
            await interaction.response.send_message(
                embed=error_embed(
                    "❌ Unlock Failed",
                    "Discord denied the channel unlock. Check my permissions."
                ),
                ephemeral=True
            )

        except discord.HTTPException as e:
            print(f"Unlock error: {e}")

            await interaction.response.send_message(
                embed=error_embed(
                    "❌ Unlock Failed",
                    "An error occurred while attempting to unlock this channel."
                ),
                ephemeral=True
            )

async def setup(bot: commands.Bot):
    await bot.add_cog(Unlock(bot))