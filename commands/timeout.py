# KaroDevGroup
# Josh Karo

import discord
from discord.ext import commands
from datetime import datetime, timedelta, timezone
from utils.embeds import success_embed, error_embed


GUILD_ID = 908868924488171540
TIMEOUT_LOG_CHANNEL_ID = 1476553088172163295

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

    def parse_duration(
        self,
        duration: str
    ):
        try:
            duration = duration.lower().strip()

            if duration.endswith("m"):
                amount = int(duration[:-1])
                timeout_duration = timedelta(
                    minutes=amount
                )

            elif duration.endswith("h"):
                amount = int(duration[:-1])
                timeout_duration = timedelta(
                    hours=amount
                )

            elif duration.endswith("d"):
                amount = int(duration[:-1])
                timeout_duration = timedelta(
                    days=amount
                )

            elif duration.endswith("w"):
                amount = int(duration[:-1])
                timeout_duration = timedelta(
                    weeks=amount
                )

            else:
                return {
                    "success": False,
                    "message":
                        "Use `m` for minutes, `h` for hours, "
                        "`d` for days, or `w` for weeks. "
                        "Examples: `10m`, `2h`, `3d`, `1w`"
                }

            if amount <= 0:
                return {
                    "success": False,
                    "message":
                        "Invalid duration. Examples: "
                        "`10m`, `2h`, `3d`, `1w`"
                }

            if timeout_duration > timedelta(days=28):
                return {
                    "success": False,
                    "message":
                        "The maximum timeout duration is 28 days."
                }

            return {
                "success": True,
                "duration_text": duration,
                "timeout_duration":timeout_duration
            }

        except ValueError:
            return {
                "success": False,
                "message":
                    "Invalid duration. Examples: "
                    "`10m`, `2h`, `3d`, `1w`"
            }

    async def send_timeout_log(
        self,
        guild: discord.Guild,
        moderator: discord.Member,
        member: discord.Member,
        duration: str,
        reason: str
    ):
        log_channel = guild.get_channel(
            TIMEOUT_LOG_CHANNEL_ID
        )

        if log_channel is None:
            try:
                log_channel = await self.bot.fetch_channel(
                    TIMEOUT_LOG_CHANNEL_ID
                )
            except (
                discord.NotFound,
                discord.Forbidden,
                discord.HTTPException
            ):
                print(
                    "[Timeout] Could not find "
                    "timeout log channel."
                )
                return

        embed = discord.Embed(
            title="🔇 Member Timed Out",
            description=
                "A moderation timeout has been issued.",
            color=discord.Color.red(),
            timestamp=datetime.now(
                timezone.utc
            )
        )

        embed.add_field(
            name="Member",
            value=(
                f"{member.mention}\n"
                f"`{member}`\n"
                f"`{member.id}`"
            ),
            inline=False
        )

        embed.add_field(
            name="Moderator",
            value=(
                f"{moderator.mention}\n"
                f"`{moderator}`\n"
                f"`{moderator.id}`"
            ),
            inline=False
        )

        embed.add_field(
            name="Duration",
            value=f"`{duration}`",
            inline=True
        )

        embed.add_field(
            name="Reason",
            value=reason,
            inline=False
        )

        embed.set_footer(
            text="Da Boyz • Moderation System"
        )

        try:
            await log_channel.send(
                embed=embed
            )

        except discord.Forbidden:
            print(
                "[Timeout] Missing permission to "
                "send messages in the timeout log channel."
            )

        except discord.HTTPException as error:
            print(
                "[Timeout] Failed to send timeout log: "
                f"{error}"
            )

    async def issue_timeout(
        self,
        guild: discord.Guild,
        moderator: discord.Member,
        member: discord.Member,
        duration: str,
        reason: str
    ):

        if not any(
            role.id in TIMEOUT_ROLE_IDS
            for role in moderator.roles
        ):
            return {
                "success": False,
                "message":
                    "You don't have permission "
                    "to timeout members."
            }

        bot_member = guild.me

        if bot_member is None:
            return {
                "success": False,
                "message":
                    "The bot could not determine "
                    "its server role."
            }

        if not bot_member.guild_permissions.moderate_members:
            return {
                "success": False,
                "message":
                    "I don't have permission "
                    "to timeout members."
            }

        if member.id == guild.owner_id:
            return {
                "success": False,
                "message":
                    "You cannot timeout the server owner."
            }

        if member.id == moderator.id:
            return {
                "success": False,
                "message":
                    "You cannot timeout yourself."
            }

        if member.top_role >= bot_member.top_role:
            return {
                "success": False,
                "message":
                    "I cannot timeout this member because "
                    "their highest role is equal to or "
                    "higher than my highest role."
            }

        parsed_duration = self.parse_duration(
            duration 
        )

        if not parsed_duration["success"]:
            return parsed_duration

        duration_text = parsed_duration[
            "duration_text"
        ]

        timeout_duration = parsed_duration[
            "timeout_duration"
        ]

        try:
            await member.timeout(
                timeout_duration,
                reason=(
                    f"{reason} | "
                    f"Timed out by {moderator}"
                )
            )

        except discord.Forbidden:
            return {
                "success": False,
                "message":
                    "Discord denied the timeout. "
                    "Check my role position and permissions."
            }

        except discord.HTTPException as error:
            print(
                f"Timeout error: {error}"
            )

            return {
                "success": False,
                "message":
                    "An error occurred while attempting "
                    "to timeout this member."
            }

        await self.send_timeout_log(
            guild=guild,
            moderator=moderator,
            member=member,
            duration=duration_text,
            reason=reason
        )

        return {
            "success": True,
            "member": member,
            "moderator": moderator,
            "duration": duration_text,
            "reason": reason
        }

    @discord.app_commands.command(
        name="timeout",
        description="Timeout a member from the server."
    )
    @discord.app_commands.guilds(
        discord.Object(
            id=GUILD_ID
        )
    )
    async def timeout(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        duration: str,
        reason: str = "No reason provided"
    ):
        guild = interaction.guild

        if guild is None:
            await interaction.response.send_message(
                embed=error_embed(
                    "❌ Action Denied",
                    "This command can only be used "
                    "inside the server."
                ),
                ephemeral=True
            )
            return

        moderator = interaction.user

        if not isinstance(
            moderator,
            discord.Member
        ):
            await interaction.response.send_message(
                embed=error_embed(
                    "❌ Action Denied",
                    "Unable to identify the moderator."
                ),
                ephemeral=True
            )
            return

        result = await self.issue_timeout(
            guild=guild,
            moderator=moderator,
            member=member,
            duration=duration,
            reason=reason
        )

        if not result["success"]:
            await interaction.response.send_message(
                embed=error_embed(
                    "❌ Timeout Failed",
                    result["message"]
                ),
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            embed=success_embed(
                "🔇 Member Timed Out",
                f"**Member:** {member}\n"
                f"**Duration:** {result['duration']}\n"
                f"**Reason:** {reason}\n"
                f"**Moderator:** {moderator}"
            )
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(
        Timeout(bot)
    )