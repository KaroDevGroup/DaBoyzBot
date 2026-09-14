# KaroDevGroup
# Josh Karo 

import discord
from discord.ext import commands
from datetime import datetime, timezone
from utils.embeds import success_embed, error_embed


GUILD_ID = 908868924488171540
CLEAR_LOG_CHANNEL_ID = 1476553088172163295

CLEAR_ROLE_IDS = {
    1006808943315648602,  # Staff
    1541650077624307772,  # Senior Staff
    1546298106763804832,  # Management
    908882405153202236,   # Owner
}

class Clear(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def send_clear_log(
        self,
        guild: discord.Guild,
        moderator: discord.Member,
        channel: discord.TextChannel,
        amount_requested: int,
        deleted_count: int
    ):
        log_channel = guild.get_channel(
            CLEAR_LOG_CHANNEL_ID
        )

        if log_channel is None:
            try:
                log_channel = await self.bot.fetch_channel(
                    CLEAR_LOG_CHANNEL_ID
                )
            except (
                discord.NotFound,
                discord.Forbidden,
                discord.HTTPException
            ):
                print(
                    "[Clear] Could not find clear log channel."
                )
                return

        embed = discord.Embed(
            title="🧹 Messages Cleared",
            description="A moderation message clear has been issued.",
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
            name="Requested",
            value=f"`{amount_requested}`",
            inline=True
        )

        embed.add_field(
            name="Deleted",
            value=f"`{deleted_count}`",
            inline=True
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
                "[Clear] Missing permission to send "
                "messages in the clear log channel."
            )

        except discord.HTTPException as error:
            print(
                "[Clear] Failed to send clear log: "
                f"{error}"
            )

    async def issue_clear(
        self,
        guild: discord.Guild,
        moderator: discord.Member,
        channel: discord.TextChannel,
        amount: int
    ):

        if not any(
            role.id in CLEAR_ROLE_IDS
            for role in moderator.roles
        ):
            return {
                "success": False,
                "message":
                    "You don't have permission to clear messages."
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


        if not permissions.manage_messages:
            return {
                "success": False,
                "message":
                    "I don't have permission to delete messages "
                    "in that channel."
            }

        if amount < 1:
            return {
                "success": False,
                "message":
                    "You must specify at least 1 message."
            }


        if amount > 100:
            return {
                "success": False,
                "message":
                    "You can only delete up to 100 messages at a time."
            }

        try:
            deleted = await channel.purge(
                limit=amount
            )

        except discord.Forbidden:
            return {
                "success": False,
                "message":
                    "Discord denied the message deletion. "
                    "Check my permissions."
            }

        except discord.HTTPException as error:
            print(
                f"Clear error: {error}"
            )

            return {
                "success": False,
                "message":
                    "An error occurred while attempting "
                    "to delete messages."
            }

        deleted_count = len(
            deleted
        )

        await self.send_clear_log(
            guild=guild,
            moderator=moderator,
            channel=channel,
            amount_requested=amount,
            deleted_count=deleted_count
        )

        return {
            "success": True,
            "channel": channel,
            "moderator": moderator,
            "amount_requested": amount,
            "deleted_count": deleted_count
        }

    @discord.app_commands.command(
        name="clear",
        description="Delete messages from the current channel."
    )
    @discord.app_commands.guilds(
        discord.Object(
            id=GUILD_ID
        )
    )
    async def clear(
        self,
        interaction: discord.Interaction,
        amount: int
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

        await interaction.response.defer()

        result = await self.issue_clear(
            guild=guild,
            moderator=moderator,
            channel=channel,
            amount=amount
        )

        if not result["success"]:
            await interaction.followup.send(
                embed=error_embed(
                    "❌ Clear Failed",
                    result["message"]
                ),
                ephemeral=True
            )
            return

        await interaction.followup.send(
            embed=success_embed(
                "🧹 Messages Cleared",
                f"**Deleted:** {result['deleted_count']} message(s)\n"
                f"**Channel:** {channel.name}\n"
                f"**Moderator:** {moderator}"
            )
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(
        Clear(bot)
    )