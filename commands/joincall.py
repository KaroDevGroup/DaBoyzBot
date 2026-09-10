# KaroDevGroup

import discord
from discord.ext import commands
from utils.embeds import success_embed, error_embed, info_embed

GUILD_ID = 908868924488171540

class JoinCall(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.app_commands.command(
        name="joincall",
        description="Joins your current voice channel."
    )
    @discord.app_commands.guilds(discord.Object(id=GUILD_ID))
    async def joincall(self, interaction: discord.Interaction):

        if not isinstance(interaction.user, discord.Member):
            await interaction.response.send_message(
                embed=error_embed(
                    "❌ Join Call Failed",
                    "I couldn't determine your server membership."
                ),
                ephemeral=True
            )
            return

        if interaction.user.voice is None or interaction.user.voice.channel is None:
            await interaction.response.send_message(
                embed=error_embed(
                    "❌ Not In Voice",
                    "You need to be in a voice channel first."
                ),
                ephemeral=True
            )
            return

        voice_channel = interaction.user.voice.channel

        await interaction.response.send_message(
            embed=info_embed(
                "🎙️ Joining Voice Channel",
                f"Joining **{voice_channel.name}**..."
            )
        )

        try:
            await voice_channel.connect()

        except Exception as e:
            print(f"Voice connection error: {e}")

            await interaction.followup.send(
                embed=error_embed(
                    "❌ Voice Connection Failed",
                    "I couldn't connect to that voice channel."
                ),
                ephemeral=True
            )

async def setup(bot: commands.Bot):
    await bot.add_cog(JoinCall(bot))