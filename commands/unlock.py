# KaroDevGroup
# Josh Karo

import discord
from discord.ext import commands
from datetime import datetime, timezone
from utils.embeds import success_embed, error_embed


GUILD_ID = 908868924488171540
UNLOCK_LOG_CHANNEL_ID = 1476553088172163295

UNLOCK_ROLE_IDS = {
    1541650077624307772,  # Senior Staff
    1546298106763804832,  # Management
    908882405153202236,   # Owner
}

class Unlock(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def send_unlock_log(
        self,
        guild: discord.Guild,
        moderator: discord.Member,
        channel: discord.TextChannel
    ):
        log_channel = guild.get_channel(
            UNLOCK_LOG_CHANNEL_ID
        )

        if log_channel is None:
            try:
                log_channel = await self.bot.fetch_channel(
                    UNLOCK_LOG_CHANNEL_ID
                )
            except (
                discord.NotFound,
                discord.Forbidden,
                discord.HTTPException
            ):
                print(
                    "[Unlock] Could not find unlock log channel."
                )
                return

        embed = discord.Embed(
            title="🔓 Channel Unlocked",
            description="A moderation channel unlock has been issued.",
            color=discord.Color.red(),
            timestamp=datetime.now(
                timezone.utc
            )
        )

        embed.add_field(
            name="Channel",
            value=(
                f"{channel.mention}\n"
                f"`{channel.name}`\n"
                f"`{channel.id}`"
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
            name="Action",
            value="Members can now send messages again.",
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
                "[Unlock] Missing permission to send "
                "messages in the unlock log channel."
            )

        except discord.HTTPException as error:
            print(
                "[Unlock] Failed to send unlock log: "
                f"{error}"
            )

    async def issue_unlock(
        self,
        guild: discord.Guild,
        moderator: discord.Member,
        channel: discord.TextChannel
    ):

        if not any(
            role.id in UNLOCK_ROLE_IDS
            for role in moderator.roles
        ):
            return {
                "success": False,
                "message":
                    "You don't have permission to unlock channels."
            }

        bot_member = guild.me

        if bot_member is None:
            return {
                "success": False,
                "message":
                    "The bot could not determine its server role."
            }

        permissions = channel.permissions_for(
            bot_member
        )

        if not permissions.manage_channels:
            return {
                "success": False,
                "message":
                    "I don't have permission to manage this channel."
            }

        try:
            overwrite = channel.overwrites_for(
                guild.default_role
            )

            overwrite.send_messages = None


            await channel.set_permissions(
                guild.default_role,
                overwrite=overwrite,
                reason=(
                    f"Channel unlocked by {moderator}"
                )
            )

        except discord.Forbidden:
            return {
                "success": False,
                "message":
                    "Discord denied the channel unlock. "
                    "Check my permissions."
            }

        except discord.HTTPException as error:
            print(
                f"Unlock error: {error}"
            )

            return {
                "success": False,
                "message":
                    "An error occurred while attempting "
                    "to unlock this channel."
            }

        await self.send_unlock_log(
            guild=guild,
            moderator=moderator,
            channel=channel
        )

        return {
            "success": True,
            "channel": channel,
            "moderator": moderator
        }

    @discord.app_commands.command(
        name="unlock",
        description="Unlock the current channel."
    )
    @discord.app_commands.guilds(
        discord.Object(
            id=GUILD_ID
        )
    )
    async def unlock(
        self,
        interaction: discord.Interaction
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

        channel = interaction.channel

        if not isinstance(
            channel,
            discord.TextChannel
        ):
            await interaction.response.send_message(
                embed=error_embed(
                    "❌ Invalid Channel",
                    "This command can only be used in a text channel."
                ),
                ephemeral=True
            )
            return

        result = await self.issue_unlock(
            guild=guild,
            moderator=moderator,
            channel=channel
        )

        if not result["success"]:
            await interaction.response.send_message(
                embed=error_embed(
                    "❌ Unlock Failed",
                    result["message"]
                ),
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            embed=success_embed(
                "🔓 Channel Unlocked",
                f"**Channel:** {channel.name}\n\n"
                "Members can now send messages in this channel."
            )
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(
        Unlock(bot)
    )