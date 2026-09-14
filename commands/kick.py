# KaroDevGroup
# Josh Karo

import discord
from discord.ext import commands
from datetime import datetime, timezone
from utils.embeds import success_embed, error_embed


GUILD_ID = 908868924488171540
KICK_LOG_CHANNEL_ID = 1476553088172163295

KICK_ROLE_IDS = {
    1006808943315648602,  # Staff
    1541650077624307772,  # Senior Staff
    1546298106763804832,  # Management
    908882405153202236,   # Owner
}

class Kick(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def send_kick_log(
        self,
        guild: discord.Guild,
        moderator: discord.Member,
        member: discord.Member,
        reason: str
    ):
        log_channel = guild.get_channel(
            KICK_LOG_CHANNEL_ID
        )

        if log_channel is None:
            try:
                log_channel = await self.bot.fetch_channel(
                    KICK_LOG_CHANNEL_ID
                )
            except (
                discord.NotFound,
                discord.Forbidden,
                discord.HTTPException
            ):
                print(
                    "[Kick] Could not find kick log channel."
                )
                return

        embed = discord.Embed(
            title="👢 Member Kicked",
            description="A moderation kick has been issued.",
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
                "[Kick] Missing permission to send "
                "messages in the kick log channel."
            )

        except discord.HTTPException as error:
            print(
                "[Kick] Failed to send kick log: "
                f"{error}"
            )

    async def issue_kick(
        self,
        guild: discord.Guild,
        moderator: discord.Member,
        member: discord.Member,
        reason: str
    ):

        if not any(
            role.id in KICK_ROLE_IDS
            for role in moderator.roles
        ):
            return {
                "success": False,
                "message":
                    "You don't have permission to kick members."
            }

        bot_member = guild.me

        if bot_member is None:
            return {
                "success": False,
                "message":
                    "The bot could not determine its server role."
            }

        if not bot_member.guild_permissions.kick_members:
            return {
                "success": False,
                "message":
                    "I don't have permission to kick members."
            }

        if member.id == guild.owner_id:
            return {
                "success": False,
                "message":
                    "You cannot kick the server owner."
            }

        if member.id == moderator.id:
            return {
                "success": False,
                "message":
                    "You cannot kick yourself."
            }

        if member.top_role >= bot_member.top_role:
            return {
                "success": False,
                "message":
                    "I cannot kick this member because "
                    "their highest role is equal to or "
                    "higher than my highest role."
            }

        try:
            await member.kick(
                reason=(
                    f"{reason} | "
                    f"Kicked by {moderator}"
                )
            )

        except discord.Forbidden:
            return {
                "success": False,
                "message":
                    "Discord denied the kick. "
                    "Check my role position and permissions."
            }

        except discord.HTTPException as error:
            print(
                f"Kick error: {error}"
            )

            return {
                "success": False,
                "message":
                    "An error occurred while attempting "
                    "to kick this member."
            }

        await self.send_kick_log(
            guild=guild,
            moderator=moderator,
            member=member,
            reason=reason
        )

        return {
            "success": True,
            "member": member,
            "moderator": moderator,
            "reason": reason
        }

    @discord.app_commands.command(
        name="kick",
        description="Kick a member from the server."
    )
    @discord.app_commands.guilds(
        discord.Object(
            id=GUILD_ID
        )
    )
    async def kick(
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

        result = await self.issue_kick(
            guild=guild,
            moderator=moderator,
            member=member,
            reason=reason
        )

        if not result["success"]:
            await interaction.response.send_message(
                embed=error_embed(
                    "❌ Kick Failed",
                    result["message"]
                ),
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            embed=success_embed(
                "👢 Member Kicked",
                f"**Member:** {member}\n"
                f"**Reason:** {reason}\n"
                f"**Moderator:** {moderator}"
            )
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(
        Kick(bot)
    )