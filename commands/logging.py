# KaroDevGroup
# Josh Karo

import discord
from discord.ext import commands
from datetime import datetime, timezone


GUILD_ID = 908868924488171540

ADMIN_LOGS_CHANNEL_ID = 1476559376163803250
CHANNEL_LOGS_CHANNEL_ID = 1476559697787228201
JOIN_LOGS_CHANNEL_ID = 1476559518837243995
LEAVE_LOGS_CHANNEL_ID = 1476559553804894362
VC_LOGS_CHANNEL_ID = 1476559645874061474
ROLE_LOGS_CHANNEL_ID = 1476559589259481240
MESSAGE_LOGS_CHANNEL_ID = 1476559466169110549


def utc_timestamp():
    return datetime.now(timezone.utc)


async def send_log(
    guild: discord.Guild | None,
    channel_id: int,
    embed: discord.Embed
):
    if guild is None:
        return

    channel = guild.get_channel(channel_id)

    if not isinstance(
        channel,
        discord.TextChannel
    ):
        return

    try:
        await channel.send(
            embed=embed,
            allowed_mentions=discord.AllowedMentions.none()
        )

    except discord.HTTPException as ex:
        print(
            f"Failed to send log to {channel_id}: {ex}"
        )

def make_embed(
    title: str,
    color: discord.Color = discord.Color.from_rgb(224, 0, 0)
):
    embed = discord.Embed(
        title=title,
        color=color,
        timestamp=utc_timestamp()
    )

    embed.set_footer(
        text="Da Boyz Logging System"
    )

    return embed

class Logging(commands.Cog):
    def __init__(
        self,
        bot: commands.Bot
    ):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(
        self,
        member: discord.Member
    ):
        if member.guild.id != GUILD_ID:
            return

        embed = make_embed(
            "📥 Member Joined",
            discord.Color.green()
        )

        embed.set_thumbnail(
            url=member.display_avatar.url
        )

        embed.add_field(
            name="User",
            value=(
                f"{member.mention}\n"
                f"`{member}`"
            ),
            inline=False
        )

        embed.add_field(
            name="User ID",
            value=f"`{member.id}`",
            inline=True
        )

        embed.add_field(
            name="Account Created",
            value=discord.utils.format_dt(
                member.created_at,
                style="F"
            ),
            inline=False
        )

        embed.add_field(
            name="Member Count",
            value=str(
                member.guild.member_count
            ),
            inline=True
        )

        await send_log(
            member.guild,
            JOIN_LOGS_CHANNEL_ID,
            embed
        )

    @commands.Cog.listener()
    async def on_member_remove(
        self,
        member: discord.Member
    ):
        if member.guild.id != GUILD_ID:
            return

        embed = make_embed(
            "📤 Member Left",
            discord.Color.dark_red()
        )

        embed.set_thumbnail(
            url=member.display_avatar.url
        )

        embed.add_field(
            name="User",
            value=(
                f"{member.mention}\n"
                f"`{member}`"
            ),
            inline=False
        )

        embed.add_field(
            name="User ID",
            value=f"`{member.id}`",
            inline=True
        )

        embed.add_field(
            name="Joined Server",
            value=(
                discord.utils.format_dt(
                    member.joined_at,
                    style="F"
                )
                if member.joined_at
                else "Unknown"
            ),
            inline=False
        )

        embed.add_field(
            name="Member Count",
            value=str(
                member.guild.member_count
            ),
            inline=True
        )

        await send_log(
            member.guild,
            LEAVE_LOGS_CHANNEL_ID,
            embed
        )

    @commands.Cog.listener()
    async def on_message_delete(
        self,
        message: discord.Message
    ):
        if message.guild is None:
            return

        if message.guild.id != GUILD_ID:
            return

        if message.author.bot:
            return

        if message.channel.id == MESSAGE_LOGS_CHANNEL_ID:
            return

        embed = make_embed(
            "🗑️ Message Deleted",
            discord.Color.dark_red()
        )

        embed.add_field(
            name="Author",
            value=(
                f"{message.author.mention}\n"
                f"`{message.author.id}`"
            ),
            inline=False
        )

        embed.add_field(
            name="Channel",
            value=message.channel.mention,
            inline=False
        )

        content = (
            message.content.strip()
            if message.content
            else "*No text content*"
        )

        if len(content) > 1000:
            content = content[:997] + "..."

        embed.add_field(
            name="Message",
            value=content,
            inline=False
        )

        if message.attachments:
            attachments = "\n".join(
                attachment.url
                for attachment in message.attachments
            )

            if len(attachments) > 1000:
                attachments = attachments[:997] + "..."

            embed.add_field(
                name="Attachments",
                value=attachments,
                inline=False
            )

        await send_log(
            message.guild,
            MESSAGE_LOGS_CHANNEL_ID,
            embed
        )

    @commands.Cog.listener()
    async def on_message_edit(
        self,
        before: discord.Message,
        after: discord.Message
    ):
        if before.guild is None:
            return

        if before.guild.id != GUILD_ID:
            return

        if before.author.bot:
            return

        if before.channel.id == MESSAGE_LOGS_CHANNEL_ID:
            return

        if before.content == after.content:
            return

        old_content = (
            before.content.strip()
            if before.content
            else "*No text content*"
        )

        new_content = (
            after.content.strip()
            if after.content
            else "*No text content*"
        )

        if len(old_content) > 1000:
            old_content = old_content[:997] + "..."

        if len(new_content) > 1000:
            new_content = new_content[:997] + "..."

        embed = make_embed(
            "✏️ Message Edited",
            discord.Color.orange()
        )

        embed.add_field(
            name="Author",
            value=(
                f"{before.author.mention}\n"
                f"`{before.author.id}`"
            ),
            inline=False
        )

        embed.add_field(
            name="Channel",
            value=before.channel.mention,
            inline=False
        )

        embed.add_field(
            name="Before",
            value=old_content,
            inline=False
        )

        embed.add_field(
            name="After",
            value=new_content,
            inline=False
        )

        embed.add_field(
            name="Message",
            value=f"[Jump to message]({after.jump_url})",
            inline=False
        )

        await send_log(
            before.guild,
            MESSAGE_LOGS_CHANNEL_ID,
            embed
        )

    @commands.Cog.listener()
    async def on_guild_channel_create(
        self,
        channel
    ):
        if channel.guild.id != GUILD_ID:
            return

        embed = make_embed(
            "➕ Channel Created",
            discord.Color.green()
        )

        embed.add_field(
            name="Channel",
            value=(
                f"{channel.mention}\n"
                f"`{channel.name}`"
            ),
            inline=False
        )

        embed.add_field(
            name="Channel ID",
            value=f"`{channel.id}`",
            inline=True
        )

        embed.add_field(
            name="Type",
            value=str(channel.type),
            inline=True
        )

        if channel.category:
            embed.add_field(
                name="Category",
                value=channel.category.name,
                inline=False
            )

        await send_log(
            channel.guild,
            CHANNEL_LOGS_CHANNEL_ID,
            embed
        )

    @commands.Cog.listener()
    async def on_guild_channel_delete(
        self,
        channel
    ):
        if channel.guild.id != GUILD_ID:
            return

        embed = make_embed(
            "➖ Channel Deleted",
            discord.Color.dark_red()
        )

        embed.add_field(
            name="Channel",
            value=f"`{channel.name}`",
            inline=False
        )

        embed.add_field(
            name="Channel ID",
            value=f"`{channel.id}`",
            inline=True
        )

        embed.add_field(
            name="Type",
            value=str(channel.type),
            inline=True
        )

        if channel.category:
            embed.add_field(
                name="Category",
                value=channel.category.name,
                inline=False
            )

        await send_log(
            channel.guild,
            CHANNEL_LOGS_CHANNEL_ID,
            embed
        )

    @commands.Cog.listener()
    async def on_guild_channel_update(
        self,
        before,
        after
    ):
        if after.guild.id != GUILD_ID:
            return

        changes = []

        if before.name != after.name:
            changes.append(
                f"**Name**\n"
                f"`{before.name}` → `{after.name}`"
            )

        if before.category != after.category:
            old_category = (
                before.category.name
                if before.category
                else "None"
            )

            new_category = (
                after.category.name
                if after.category
                else "None"
            )

            changes.append(
                f"**Category**\n"
                f"`{old_category}` → `{new_category}`"
            )

        if hasattr(before, "topic") and hasattr(after, "topic"):
            if before.topic != after.topic:
                changes.append(
                    "**Topic changed**"
                )

        if not changes:
            return

        embed = make_embed(
            "⚙️ Channel Updated",
            discord.Color.orange()
        )

        embed.add_field(
            name="Channel",
            value=after.mention,
            inline=False
        )

        embed.add_field(
            name="Changes",
            value="\n\n".join(changes),
            inline=False
        )

        await send_log(
            after.guild,
            CHANNEL_LOGS_CHANNEL_ID,
            embed
        )

    @commands.Cog.listener()
    async def on_guild_role_create(
        self,
        role: discord.Role
    ):
        if role.guild.id != GUILD_ID:
            return

        embed = make_embed(
            "➕ Role Created",
            discord.Color.green()
        )

        embed.add_field(
            name="Role",
            value=(
                f"{role.mention}\n"
                f"`{role.name}`"
            ),
            inline=False
        )

        embed.add_field(
            name="Role ID",
            value=f"`{role.id}`",
            inline=True
        )

        await send_log(
            role.guild,
            ROLE_LOGS_CHANNEL_ID,
            embed
        )

    @commands.Cog.listener()
    async def on_guild_role_delete(
        self,
        role: discord.Role
    ):
        if role.guild.id != GUILD_ID:
            return

        embed = make_embed(
            "➖ Role Deleted",
            discord.Color.dark_red()
        )

        embed.add_field(
            name="Role",
            value=f"`{role.name}`",
            inline=False
        )

        embed.add_field(
            name="Role ID",
            value=f"`{role.id}`",
            inline=True
        )

        await send_log(
            role.guild,
            ROLE_LOGS_CHANNEL_ID,
            embed
        )

    @commands.Cog.listener()
    async def on_guild_role_update(
        self,
        before: discord.Role,
        after: discord.Role
    ):
        if after.guild.id != GUILD_ID:
            return

        changes = []

        if before.name != after.name:
            changes.append(
                f"**Name**\n"
                f"`{before.name}` → `{after.name}`"
            )

        if before.color != after.color:
            changes.append(
                f"**Color**\n"
                f"`{before.color}` → `{after.color}`"
            )

        if before.permissions != after.permissions:
            changes.append(
                "**Permissions changed**"
            )

        if before.hoist != after.hoist:
            changes.append(
                f"**Displayed separately**\n"
                f"`{before.hoist}` → `{after.hoist}`"
            )

        if before.mentionable != after.mentionable:
            changes.append(
                f"**Mentionable**\n"
                f"`{before.mentionable}` → `{after.mentionable}`"
            )

        if not changes:
            return

        embed = make_embed(
            "⚙️ Role Updated",
            discord.Color.orange()
        )

        embed.add_field(
            name="Role",
            value=after.mention,
            inline=False
        )

        embed.add_field(
            name="Changes",
            value="\n\n".join(changes),
            inline=False
        )

        await send_log(
            after.guild,
            ROLE_LOGS_CHANNEL_ID,
            embed
        )

    @commands.Cog.listener()
    async def on_member_update(
        self,
        before: discord.Member,
        after: discord.Member
    ):
        if after.guild.id != GUILD_ID:
            return

        before_roles = set(
            before.roles
        )

        after_roles = set(
            after.roles
        )

        added_roles = (
            after_roles - before_roles
        )

        removed_roles = (
            before_roles - after_roles
        )

        if not added_roles and not removed_roles:
            return

        embed = make_embed(
            "👤 Member Roles Updated",
            discord.Color.orange()
        )

        embed.add_field(
            name="Member",
            value=(
                f"{after.mention}\n"
                f"`{after.id}`"
            ),
            inline=False
        )

        if added_roles:
            embed.add_field(
                name="Roles Added",
                value="\n".join(
                    role.mention
                    for role in added_roles
                    if role != after.guild.default_role
                ) or "None",
                inline=False
            )

        if removed_roles:
            embed.add_field(
                name="Roles Removed",
                value="\n".join(
                    role.mention
                    for role in removed_roles
                    if role != after.guild.default_role
                ) or "None",
                inline=False
            )

        await send_log(
            after.guild,
            ROLE_LOGS_CHANNEL_ID,
            embed
        )

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState
    ):
        if member.guild.id != GUILD_ID:
            return

        if (
            before.channel is None
            and after.channel is not None
        ):
            embed = make_embed(
                "🔊 Voice Channel Joined",
                discord.Color.green()
            )

            embed.add_field(
                name="Member",
                value=(
                    f"{member.mention}\n"
                    f"`{member.id}`"
                ),
                inline=False
            )

            embed.add_field(
                name="Channel",
                value=after.channel.mention,
                inline=False
            )

            await send_log(
                member.guild,
                VC_LOGS_CHANNEL_ID,
                embed
            )

            return

        if (
            before.channel is not None
            and after.channel is None
        ):
            embed = make_embed(
                "🔇 Voice Channel Left",
                discord.Color.dark_red()
            )

            embed.add_field(
                name="Member",
                value=(
                    f"{member.mention}\n"
                    f"`{member.id}`"
                ),
                inline=False
            )

            embed.add_field(
                name="Channel",
                value=before.channel.mention,
                inline=False
            )

            await send_log(
                member.guild,
                VC_LOGS_CHANNEL_ID,
                embed
            )

            return

        if before.channel != after.channel:
            embed = make_embed(
                "🔁 Voice Channel Moved",
                discord.Color.orange()
            )

            embed.add_field(
                name="Member",
                value=(
                    f"{member.mention}\n"
                    f"`{member.id}`"
                ),
                inline=False
            )

            embed.add_field(
                name="From",
                value=(
                    before.channel.mention
                    if before.channel
                    else "None"
                ),
                inline=True
            )

            embed.add_field(
                name="To",
                value=(
                    after.channel.mention
                    if after.channel
                    else "None"
                ),
                inline=True
            )

            await send_log(
                member.guild,
                VC_LOGS_CHANNEL_ID,
                embed
            )

            return

        changes = []

        if before.self_mute != after.self_mute:
            changes.append(
                f"Self Mute: `{before.self_mute}` → `{after.self_mute}`"
            )

        if before.self_deaf != after.self_deaf:
            changes.append(
                f"Self Deaf: `{before.self_deaf}` → `{after.self_deaf}`"
            )

        if before.mute != after.mute:
            changes.append(
                f"Server Mute: `{before.mute}` → `{after.mute}`"
            )

        if before.deaf != after.deaf:
            changes.append(
                f"Server Deaf: `{before.deaf}` → `{after.deaf}`"
            )

        if not changes:
            return

        embed = make_embed(
            "🎙️ Voice State Updated",
            discord.Color.orange()
        )

        embed.add_field(
            name="Member",
            value=(
                f"{member.mention}\n"
                f"`{member.id}`"
            ),
            inline=False
        )

        if after.channel:
            embed.add_field(
                name="Channel",
                value=after.channel.mention,
                inline=False
            )

        embed.add_field(
            name="Changes",
            value="\n".join(changes),
            inline=False
        )

        await send_log(
            member.guild,
            VC_LOGS_CHANNEL_ID,
            embed
        )

async def setup(
    bot: commands.Bot
):
    await bot.add_cog(
        Logging(bot)
    )