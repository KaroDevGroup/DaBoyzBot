# KaroDevGroup

import discord
from discord.ext import commands
from datetime import timedelta
from utils.embeds import success_embed, error_embed

GUILD_ID = 908868924488171540

TIMEOUT_ROLE_IDS = {
    1488309396797653112,  # Trial Staff
    1006808943315648602,  # Staff
    1541650077624307772,  # Senior Staff
    1546298106763804832,  # Management
    908882405153202236,   # Owner
}

class Timeout(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.app_commands.command(
        name="timeout",
        description="Timeout a member from the server."
    )
    @discord.app_commands.guilds(discord.Object(id=GUILD_ID))
    async def timeout(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        duration: str,
        reason: str = "No reason provided"
    ):
        if not any(role.id in TIMEOUT_ROLE_IDS for role in interaction.user.roles):
            await interaction.response.send_message(
                embed=error_embed(
                    "❌ Permission Denied",
                    "You don't have permission to use this command."
                ),
                ephemeral=True
            )
            return

        if not interaction.guild.me.guild_permissions.moderate_members:
            await interaction.response.send_message(
                embed=error_embed(
                    "❌ Missing Permission",
                    "I don't have permission to timeout members."
                ),
                ephemeral=True
            )
            return

        if member.id == interaction.guild.owner_id:
            await interaction.response.send_message(
                embed=error_embed(
                    "❌ Action Denied",
                    "You cannot timeout the server owner."
                ),
                ephemeral=True
            )
            return

        if member.id == interaction.user.id:
            await interaction.response.send_message(
                embed=error_embed(
                    "❌ Action Denied",
                    "You cannot timeout yourself."
                ),
                ephemeral=True
            )
            return

        if member.top_role >= interaction.guild.me.top_role:
            await interaction.response.send_message(
                embed=error_embed(
                    "❌ Action Denied",
                    "I cannot timeout this member because their highest role "
                    "is equal to or higher than my highest role."
                ),
                ephemeral=True
            )
            return

        try:
            duration = duration.lower().strip()

            if duration.endswith("m"):
                amount = int(duration[:-1])
                timeout_duration = timedelta(minutes=amount)

            elif duration.endswith("h"):
                amount = int(duration[:-1])
                timeout_duration = timedelta(hours=amount)

            elif duration.endswith("d"):
                amount = int(duration[:-1])
                timeout_duration = timedelta(days=amount)

            elif duration.endswith("w"):
                amount = int(duration[:-1])
                timeout_duration = timedelta(weeks=amount)

            else:
                await interaction.response.send_message(
                    embed=error_embed(
                        "❌ Invalid Duration",
                        "Use `m` for minutes, `h` for hours, `d` for days, "
                        "or `w` for weeks.\n\n"
                        "Examples: `10m`, `2h`, `3d`, `1w`"
                    ),
                    ephemeral=True
                )
                return

            if amount <= 0:
                raise ValueError

            if timeout_duration > timedelta(days=28):
                await interaction.response.send_message(
                    embed=error_embed(
                        "❌ Invalid Duration",
                        "The maximum timeout duration is **28 days**."
                    ),
                    ephemeral=True
                )
                return

        except ValueError:
            await interaction.response.send_message(
                embed=error_embed(
                    "❌ Invalid Duration",
                    "Invalid duration. Examples: `10m`, `2h`, `3d`, `1w`"
                ),
                ephemeral=True
            )
            return

        try:
            await member.timeout(
                timeout_duration,
                reason=f"{reason} | Timed out by {interaction.user}"
            )

            await interaction.response.send_message(
                embed=success_embed(
                    "🔇 Member Timed Out",
                    f"**Member:** {member}\n"
                    f"**Duration:** {duration}\n"
                    f"**Reason:** {reason}\n"
                    f"**Moderator:** {interaction.user}"
                )
            )

        except discord.Forbidden:
            await interaction.response.send_message(
                embed=error_embed(
                    "❌ Timeout Failed",
                    "Discord denied the timeout. Check my role position and permissions."
                ),
                ephemeral=True
            )

        except discord.HTTPException as e:
            print(f"Timeout error: {e}")

            await interaction.response.send_message(
                embed=error_embed(
                    "❌ Timeout Failed",
                    "An error occurred while attempting to timeout this member."
                ),
                ephemeral=True
            )

async def setup(bot: commands.Bot):
    await bot.add_cog(Timeout(bot))