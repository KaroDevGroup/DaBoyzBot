# KaroDevGroup
# Josh Karo 

import discord
from discord.ext import commands
from utils.embeds import info_embed


GUILD_ID = 908868924488171540
GITHUB_REPO = "https://github.com/KaroDevGroup/DaBoyzApp"

class Download(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.app_commands.command(
        name="download",
        description="Get the latest DaBoyzApp download."
    )
    @discord.app_commands.guilds(discord.Object(id=GUILD_ID))
    async def download(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            embed=info_embed(
                "📥 DaBoyzApp Download",
                f"Download the latest version of **DaBoyzApp** here:\n\n"
                f"{GITHUB_REPO}"
            )
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(Download(bot))