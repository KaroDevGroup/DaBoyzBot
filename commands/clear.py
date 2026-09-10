# KaroDevGroup

import discord
from discord.ext import commands
from utils.embeds import success_embed, error_embed

GUILD_ID = 908868924488171540

CLEAR_ROLE_IDS = {
    1006808943315648602,  # Staff
    1541650077624307772,  # Senior Staff
    1546298106763804832,  # Management
    908882405153202236,   # Owner
}

class Clear(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.app_commands.command(
        name="clear",
        description="Delete messages from the current channel."
    )
    @discord.app_commands.guilds(discord.Object(id=GUILD_ID))
    async def clear(
        self,
        interaction: discord.Interaction,
        amount: int
    ):
        if not any(role.id in CLEAR_ROLE_IDS for role in interaction.user.roles):
            await interaction.response.send_message(
                embed=error_embed(
                    "❌ Permission Denied",
                    "You don't have permission to use this command."
                ),
                ephemeral=True
            )
            return

        if not interaction.guild.me.guild_permissions.manage_messages:
            await interaction.response.send_message(
                embed=error_embed(
                    "❌ Missing Permission",
                    "I don't have permission to delete messages."
                ),
                ephemeral=True
            )
            return

        if amount < 1:
            await interaction.response.send_message(
                embed=error_embed(
                    "❌ Invalid Amount",
                    "You must specify at least 1 message."
                ),
                ephemeral=True
            )
            return

        if amount > 100:
            await interaction.response.send_message(
                embed=error_embed(
                    "❌ Invalid Amount",
                    "You can only delete up to **100 messages** at a time."
                ),
                ephemeral=True
            )
            return

        try:
            await interaction.response.defer()

            deleted = await interaction.channel.purge(
                limit=amount
            )

            await interaction.followup.send(
                embed=success_embed(
                    "🧹 Messages Cleared",
                    f"**Deleted:** {len(deleted)} message(s)\n"
                    f"**Channel:** {interaction.channel.name}\n"
                    f"**Moderator:** {interaction.user}"
                )
            )

        except discord.Forbidden:
            await interaction.followup.send(
                embed=error_embed(
                    "❌ Clear Failed",
                    "Discord denied the message deletion. "
                    "Check my permissions."
                ),
                ephemeral=True
            )

        except discord.HTTPException as e:
            print(f"Clear error: {e}")

            await interaction.followup.send(
                embed=error_embed(
                    "❌ Clear Failed",
                    "An error occurred while attempting to delete messages."
                ),
                ephemeral=True
            )

async def setup(bot: commands.Bot):
    await bot.add_cog(Clear(bot))