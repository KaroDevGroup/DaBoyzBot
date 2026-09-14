# KaroDevGroup
# Josh Karo

import discord
from discord.ext import commands
from datetime import datetime, timezone
from utils.embeds import success_embed, error_embed


GUILD_ID = 908868924488171540
UNBAN_LOG_CHANNEL_ID = 1476553088172163295

UNBAN_ROLE_IDS = {
    1546298106763804832,  # Management
    908882405153202236,   # Owner
}

class Unban(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def send_unban_log(
        self,
        guild: discord.Guild,
        moderator: discord.Member,
        user: discord.User,
        reason: str
    ):
        log_channel = guild.get_channel(
            UNBAN_LOG_CHANNEL_ID
        )

        if log_channel is None:
            try:
                log_channel = await self.bot.fetch_channel(
                    UNBAN_LOG_CHANNEL_ID
                )
            except (
                discord.NotFound,
                discord.Forbidden,
                discord.HTTPException
            ):
                print(
                    "[Unban] Could not find unban log channel."
                )
                return

        embed = discord.Embed(
            title="🔓 Member Unbanned",
            description="A moderation unban has been issued.",
            color=discord.Color.red(),
            timestamp=datetime.now(
                timezone.utc
            )
        )

        embed.add_field(
            name="User",
            value=(
                f"{user.mention}\n"
                f"`{user}`\n"
                f"`{user.id}`"
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
                "[Unban] Missing permission to send "
                "messages in the unban log channel."
            )

        except discord.HTTPException as error:
            print(
                "[Unban] Failed to send unban log: "
                f"{error}"
            )

    async def issue_unban(
        self,
        guild: discord.Guild,
        moderator: discord.Member,
        user: discord.User,
        reason: str
    ):

        if not any(
            role.id in UNBAN_ROLE_IDS
            for role in moderator.roles
        ):
            return {
                "success": False,
                "message":
                    "You don't have permission to unban members."
            }

        bot_member = guild.me

        if bot_member is None:
            return {
                "success": False,
                "message":
                    "The bot could not determine its server role."
            }

        if not bot_member.guild_permissions.ban_members:
            return {
                "success": False,
                "message":
                    "I don't have permission to unban members."
            }

        try:
            await guild.fetch_ban(
                user
            )

        except discord.NotFound:
            return {
                "success": False,
                "message":
                    f"{user} is not currently banned."
            }

        except discord.HTTPException:
            return {
                "success": False,
                "message":
                    "I couldn't check the server's ban list."
            }

        try:
            await guild.unban(
                user,
                reason=(
                    f"{reason} | "
                    f"Unbanned by {moderator}"
                )
            )

        except discord.Forbidden:
            return {
                "success": False,
                "message":
                    "Discord denied the unban. "
                    "Check my permissions."
            }

        except discord.HTTPException as error:
            print(
                f"Unban error: {error}"
            )

            return {
                "success": False,
                "message":
                    "An error occurred while attempting "
                    "to unban this user."
            }

        await self.send_unban_log(
            guild=guild,
            moderator=moderator,
            user=user,
            reason=reason
        )

        return {
            "success": True,
            "user": user,
            "moderator": moderator,
            "reason": reason
        }

    @discord.app_commands.command(
        name="unban",
        description="Unban a user from the server."
    )
    @discord.app_commands.guilds(
        discord.Object(
            id=GUILD_ID
        )
    )
    async def unban(
        self,
        interaction: discord.Interaction,
        user_id: str,
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

        try:
            user_id_int = int(
                user_id
            )

        except ValueError:
            await interaction.response.send_message(
                embed=error_embed(
                    "❌ Invalid User ID",
                    "Please provide a valid Discord User ID."
                ),
                ephemeral=True
            )
            return

        try:
            user = await self.bot.fetch_user(
                user_id_int
            )

        except discord.NotFound:
            await interaction.response.send_message(
                embed=error_embed(
                    "❌ User Not Found",
                    "I couldn't find a Discord user with that ID."
                ),
                ephemeral=True
            )
            return

        except discord.HTTPException:
            await interaction.response.send_message(
                embed=error_embed(
                    "❌ Request Failed",
                    "I couldn't retrieve that user from Discord."
                ),
                ephemeral=True
            )
            return

        result = await self.issue_unban(
            guild=guild,
            moderator=moderator,
            user=user,
            reason=reason
        )

        if not result["success"]:
            await interaction.response.send_message(
                embed=error_embed(
                    "❌ Unban Failed",
                    result["message"]
                ),
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            embed=success_embed(
                "🔓 Member Unbanned",
                f"**User:** {user}\n"
                f"**Reason:** {reason}\n"
                f"**Moderator:** {moderator}"
            )
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(
        Unban(bot)
    )