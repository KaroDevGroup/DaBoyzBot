# KaroDevGroup
# Josh Karo

import discord
from discord.ext import commands
from utils.embeds import success_embed, error_embed


GUILD_ID = 908868924488171540

SLOWMODE_ROLE_IDS = {
    1006808943315648602,  # Staff
    1541650077624307772,  # Senior Staff
    1546298106763804832,  # Management
    908882405153202236,   # Owner
}

class Slowmode(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.app_commands.command(
        name="slowmode",
        description="Set or disable slowmode in the current channel."
    )
    @discord.app_commands.guilds(discord.Object(id=GUILD_ID))
    async def slowmode(
        self,
        interaction: discord.Interaction,
        duration: str
    ):
        if not any(role.id in SLOWMODE_ROLE_IDS for role in interaction.user.roles):
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

        duration = duration.lower().strip()

        if duration == "off":
            seconds = 0

        else:
            try:
                if duration.endswith("s"):
                    amount = int(duration[:-1])
                    seconds = amount

                elif duration.endswith("m"):
                    amount = int(duration[:-1])
                    seconds = amount * 60

                elif duration.endswith("h"):
                    amount = int(duration[:-1])
                    seconds = amount * 60 * 60

                else:
                    await interaction.response.send_message(
                        embed=error_embed(
                            "❌ Invalid Duration",
                            "Use `s` for seconds, `m` for minutes, or `h` for hours.\n\n"
                            "Examples: `10s`, `1m`, `5m`, `1h`\n"
                            "Use `off` to disable slowmode."
                        ),
                        ephemeral=True
                    )
                    return

                if seconds < 1:
                    raise ValueError

            except ValueError:
                await interaction.response.send_message(
                    embed=error_embed(
                        "❌ Invalid Duration",
                        "Please provide a valid slowmode duration.\n\n"
                        "Examples: `10s`, `1m`, `5m`, `1h`\n"
                        "Use `off` to disable slowmode."
                    ),
                    ephemeral=True
                )
                return

            if seconds > 21600:
                await interaction.response.send_message(
                    embed=error_embed(
                        "❌ Invalid Duration",
                        "The maximum slowmode duration is **6 hours**."
                    ),
                    ephemeral=True
                )
                return

        channel = interaction.channel

        try:
            await channel.edit(
                slowmode_delay=seconds,
                reason=f"Slowmode changed by {interaction.user}"
            )

            if seconds == 0:
                await interaction.response.send_message(
                    embed=success_embed(
                        "🔓 Slowmode Disabled",
                        f"**Channel:** {channel.name}\n"
                        f"**Moderator:** {interaction.user}\n\n"
                        "Members can now send messages without a slowmode delay."
                    )
                )
            else:
                if seconds < 60:
                    duration_text = f"{seconds} second(s)"
                elif seconds % 3600 == 0:
                    duration_text = f"{seconds // 3600} hour(s)"
                else:
                    duration_text = f"{seconds // 60} minute(s)"

                await interaction.response.send_message(
                    embed=success_embed(
                        "🐌 Slowmode Enabled",
                        f"**Channel:** {channel.name}\n"
                        f"**Delay:** {duration_text}\n"
                        f"**Moderator:** {interaction.user}"
                    )
                )

        except discord.Forbidden:
            await interaction.response.send_message(
                embed=error_embed(
                    "❌ Slowmode Failed",
                    "Discord denied the slowmode change. Check my permissions."
                ),
                ephemeral=True
            )

        except discord.HTTPException as e:
            print(f"Slowmode error: {e}")

            await interaction.response.send_message(
                embed=error_embed(
                    "❌ Slowmode Failed",
                    "An error occurred while attempting to change slowmode."
                ),
                ephemeral=True
            )

async def setup(bot: commands.Bot):
    await bot.add_cog(Slowmode(bot))