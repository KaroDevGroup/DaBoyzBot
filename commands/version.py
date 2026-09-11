# KaroDevGroup

import discord
from discord.ext import commands
from utils.embeds import info_embed

GUILD_ID = 908868924488171540
APP_VERSION = "1.1.7"

class Version(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.app_commands.command(
        name="version",
        description="Shows the current DaBoyzApp version."
    )
    @discord.app_commands.guilds(discord.Object(id=GUILD_ID))
    async def version(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            embed=info_embed(
                "🖥️ DaBoyzApp Version",
                f"The current DaBoyzApp version is **v{APP_VERSION}**."
            )
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(Version(bot))