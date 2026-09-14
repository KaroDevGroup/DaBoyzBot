# KaroDevGroup
# Josh Karo

import discord
from discord.ext import commands
import json
import os
from datetime import datetime, timezone
from utils.embeds import success_embed, error_embed


GUILD_ID = 908868924488171540
WARN_LOG_CHANNEL_ID = 1476553088172163295

WARN_ROLE_IDS = {
    1488309396797653112,  # Trial Staff
    1006808943315648602,  # Staff
    1541650077624307772,  # Senior Staff
    1546298106763804832,  # Management
    908882405153202236,   # Owner
}

WARNINGS_FILE = "warnings.json"

class Warn(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def load_warnings(self):
        if not os.path.exists(WARNINGS_FILE):
            return {}

        try:
            with open(
                WARNINGS_FILE,
                "r",
                encoding="utf-8"
            ) as file:
                return json.load(file)

        except (json.JSONDecodeError, OSError):
            return {}

    def save_warnings(self, warnings):
        with open(
            WARNINGS_FILE,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                warnings,
                file,
                indent=4
            )

    async def send_warning_log(
        self,
        guild: discord.Guild,
        moderator: discord.Member,
        member: discord.Member,
        reason: str,
        warning_number: int
    ):
        log_channel = guild.get_channel(
            WARN_LOG_CHANNEL_ID
        )

        if log_channel is None:
            try:
                log_channel = await self.bot.fetch_channel(
                    WARN_LOG_CHANNEL_ID
                )
            except (
                discord.NotFound,
                discord.Forbidden,
                discord.HTTPException
            ):
                print(
                    "[Warn] Could not find warning log channel."
                )
                return

        embed = discord.Embed(
            title="⚠️ Member Warned",
            description="A moderation warning has been issued.",
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
            name="Warning Number",
            value=f"`#{warning_number}`",
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
                "[Warn] Missing permission to send "
                "messages in the warning log channel."
            )

        except discord.HTTPException as error:
            print(
                "[Warn] Failed to send warning log: "
                f"{error}"
            )

    async def issue_warning(
        self,
        guild: discord.Guild,
        moderator: discord.Member,
        member: discord.Member,
        reason: str
    ):

        if not any(
            role.id in WARN_ROLE_IDS
            for role in moderator.roles
        ):
            return {
                "success": False,
                "message":
                    "You don't have permission to warn members."
            }

        if member.id == guild.owner_id:
            return {
                "success": False,
                "message":
                    "You cannot warn the server owner."
            }

        if member.id == moderator.id:
            return {
                "success": False,
                "message":
                    "You cannot warn yourself."
            }

        bot_member = guild.me

        if bot_member is None:
            return {
                "success": False,
                "message":
                    "The bot could not determine its server role."
            }

        if member.top_role >= bot_member.top_role:
            return {
                "success": False,
                "message":
                    "I cannot warn this member because their highest role "
                    "is equal to or higher than my highest role."
            }

        warnings = self.load_warnings()

        user_id = str(member.id)

        if user_id not in warnings:
            warnings[user_id] = []

        warning_number = (
            len(warnings[user_id]) + 1
        )

        warning_data = {
            "id": warning_number,
            "reason": reason,
            "moderator": moderator.id,
            "moderator_name": str(moderator),
            "timestamp":
                datetime.now(
                    timezone.utc
                ).isoformat()
        }

        warnings[user_id].append(
            warning_data
        )

        self.save_warnings(
            warnings
        )

        await self.send_warning_log(
            guild=guild,
            moderator=moderator,
            member=member,
            reason=reason,
            warning_number=warning_number
        )

        return {
            "success": True,
            "warning_number": warning_number,
            "member": member,
            "moderator": moderator,
            "reason": reason
        }

    @discord.app_commands.command(
        name="warn",
        description="Warn a member."
    )
    @discord.app_commands.guilds(
        discord.Object(
            id=GUILD_ID
        )
    )
    async def warn(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str = "No reason provided"
    ):
        guild = interaction.guild

        if guild is None:
            await interaction.response.send_message(
                embed=error_embed(
                    "❌ Action Denied",
                    "This command can only be used inside the server."
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

        result = await self.issue_warning(
            guild=guild,
            moderator=moderator,
            member=member,
            reason=reason
        )

        if not result["success"]:
            await interaction.response.send_message(
                embed=error_embed(
                    "❌ Action Denied",
                    result["message"]
                ),
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            embed=success_embed(
                "⚠️ Member Warned",
                f"**Member:** {member}\n"
                f"**Warning #:** {result['warning_number']}\n"
                f"**Reason:** {reason}\n"
                f"**Moderator:** {moderator}"
            )
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(
        Warn(bot)
    )