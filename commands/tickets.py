# KaroDevGroup
# Josh Karo

import discord
from discord.ext import commands
import html
import io
from datetime import datetime, timezone
from supabase_client import supabase


GUILD_ID = 908868924488171540

TICKET_PANEL_CHANNEL_ID = 1487933916248805517
TICKET_CATEGORY_ID = 1487934719936167976

TRANSCRIPT_CHANNEL_ID = 1487935663763619860
TICKET_LOG_CHANNEL_ID = 1487935780541431859

STAFF_ROLE_ID = 1006808943315648602

STAFF_ROLE_IDS = [
    1006808943315648602,  # Staff
    1541650077624307772,  # Senior Staff
    1546298106763804832,  # Management
    908882405153202236,   # Owner
]

def is_staff(
    member: discord.Member
) -> bool:

    if member.guild_permissions.administrator:
        return True

    return any(
        role.id in STAFF_ROLE_IDS
        for role in member.roles
    )

def get_ticket_by_channel(
    channel_id: int
):
    response = (
        supabase
        .table("tickets")
        .select("*")
        .eq(
            "guild_id",
            str(GUILD_ID)
        )
        .eq(
            "channel_id",
            str(channel_id)
        )
        .limit(1)
        .execute()
    )

    if not response.data:
        return None

    return response.data[0]

async def user_has_open_ticket(
    user_id: int
) -> bool:

    response = (
        supabase
        .table("tickets")
        .select("id")
        .eq(
            "guild_id",
            str(GUILD_ID)
        )
        .eq(
            "creator_id",
            str(user_id)
        )
        .eq(
            "status",
            "open"
        )
        .limit(1)
        .execute()
    )

    return bool(
        response.data
    )

async def user_has_other_open_ticket(
    user_id: int,
    current_ticket_id: int
) -> bool:

    response = (
        supabase
        .table("tickets")
        .select("id")
        .eq(
            "guild_id",
            str(GUILD_ID)
        )
        .eq(
            "creator_id",
            str(user_id)
        )
        .eq(
            "status",
            "open"
        )
        .execute()
    )

    for row in response.data or []:
        if int(row["id"]) != int(current_ticket_id):
            return True

    return False

async def generate_html_transcript(
    channel: discord.TextChannel,
    ticket_row: dict
) -> discord.File:

    ticket_number = int(
        ticket_row["ticket_number"]
    )

    ticket_type = (
        ticket_row.get(
            "ticket_type",
            "unknown"
        )
    )

    messages = []

    async for message in channel.history(
        limit=None,
        oldest_first=True
    ):
        messages.append(
            message
        )

    message_blocks = []

    for message in messages:

        author_name = html.escape(
            str(
                message.author.display_name
            )
        )

        author_id = (
            message.author.id
        )

        avatar_url = ""

        try:
            avatar_url = str(
                message.author.display_avatar.url
            )
        except Exception:
            avatar_url = ""

        timestamp = (
            message.created_at
            .astimezone(
                timezone.utc
            )
            .strftime(
                "%Y-%m-%d %H:%M:%S UTC"
            )
        )

        content = html.escape(
            message.content or ""
        )

        content = content.replace(
            "\n",
            "<br>"
        )

        attachments_html = ""

        if message.attachments:

            attachment_links = []

            for attachment in message.attachments:

                safe_filename = html.escape(
                    attachment.filename
                )

                safe_url = html.escape(
                    attachment.url
                )

                attachment_links.append(
                    (
                        f'<a href="{safe_url}" '
                        f'target="_blank">'
                        f'{safe_filename}'
                        f'</a>'
                    )
                )

            attachments_html = (
                '<div class="attachments">'
                '<strong>Attachments:</strong><br>'
                + "<br>".join(
                    attachment_links
                )
                + "</div>"
            )


        embeds_html = ""

        if message.embeds:

            embed_items = []

            for embed in message.embeds:

                embed_title = html.escape(
                    embed.title or ""
                )

                embed_description = html.escape(
                    embed.description or ""
                ).replace(
                    "\n",
                    "<br>"
                )

                embed_html = (
                    '<div class="embed">'
                )

                if embed_title:
                    embed_html += (
                        f'<div class="embed-title">'
                        f'{embed_title}'
                        f'</div>'
                    )

                if embed_description:
                    embed_html += (
                        f'<div class="embed-description">'
                        f'{embed_description}'
                        f'</div>'
                    )

                embed_html += "</div>"

                embed_items.append(
                    embed_html
                )

            embeds_html = "".join(
                embed_items
            )


        avatar_html = ""

        if avatar_url:
            avatar_html = (
                f'<img class="avatar" '
                f'src="{html.escape(avatar_url)}">'
            )


        message_blocks.append(
            f"""
            <div class="message">
                <div class="avatar-area">
                    {avatar_html}
                </div>

                <div class="message-body">

                    <div class="message-header">
                        <span class="author">
                            {author_name}
                        </span>

                        <span class="author-id">
                            {author_id}
                        </span>

                        <span class="timestamp">
                            {timestamp}
                        </span>
                    </div>

                    <div class="content">
                        {content}
                    </div>

                    {attachments_html}

                    {embeds_html}

                </div>
            </div>
            """
        )


    full_html = f"""
<!DOCTYPE html>

<html lang="en">

<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width, initial-scale=1.0">

<title>
Da Boyz Ticket #{ticket_number:04d}
</title>

<style>

body {{
    margin: 0;
    padding: 0;
    background: #080808;
    color: #ffffff;
    font-family:
        Arial,
        Helvetica,
        sans-serif;
}}

.header {{
    background: #111111;
    border-bottom: 2px solid #e00000;
    padding: 25px 35px;
}}

.brand {{
    font-size: 13px;
    color: #e00000;
    font-weight: bold;
    letter-spacing: 2px;
}}

.title {{
    margin-top: 6px;
    font-size: 26px;
    font-weight: bold;
}}

.meta {{
    margin-top: 12px;
    color: #999999;
    font-size: 12px;
}}

.container {{
    max-width: 1100px;
    margin: 0 auto;
    padding: 30px;
}}

.message {{
    display: flex;
    gap: 14px;
    padding: 14px 10px;
    border-bottom: 1px solid #222222;
}}

.message:hover {{
    background: #101010;
}}

.avatar-area {{
    width: 42px;
    flex-shrink: 0;
}}

.avatar {{
    width: 40px;
    height: 40px;
    border-radius: 50%;
}}

.message-body {{
    flex: 1;
    min-width: 0;
}}

.message-header {{
    margin-bottom: 6px;
}}

.author {{
    font-weight: bold;
    color: #ffffff;
}}

.author-id {{
    margin-left: 7px;
    color: #555555;
    font-size: 10px;
}}

.timestamp {{
    margin-left: 10px;
    color: #777777;
    font-size: 11px;
}}

.content {{
    color: #d5d5d5;
    line-height: 1.5;
    word-wrap: break-word;
}}

.attachments {{
    margin-top: 10px;
    color: #aaaaaa;
    font-size: 12px;
}}

.attachments a {{
    color: #ff3333;
}}

.embed {{
    margin-top: 10px;
    padding: 12px 14px;
    background: #161616;
    border-left: 4px solid #e00000;
    border-radius: 4px;
}}

.embed-title {{
    font-weight: bold;
    margin-bottom: 5px;
}}

.embed-description {{
    color: #c7c7c7;
    line-height: 1.4;
}}

.footer {{
    padding: 25px;
    text-align: center;
    color: #555555;
    font-size: 11px;
}}

</style>

</head>

<body>

<div class="header">

    <div class="brand">
        DA BOYZ
    </div>

    <div class="title">
        Ticket #{ticket_number:04d} Transcript
    </div>

    <div class="meta">

        Channel:
        {html.escape(channel.name)}

        <br>

        Type:
        {html.escape(ticket_type)}

        <br>

        Creator ID:
        {html.escape(str(ticket_row["creator_id"]))}

    </div>

</div>


<div class="container">

    {''.join(message_blocks)}

</div>


<div class="footer">

    Generated by DaBoyzBot

</div>


</body>

</html>
"""

    transcript_bytes = (
        full_html.encode(
            "utf-8"
        )
    )

    buffer = io.BytesIO(
        transcript_bytes
    )

    return discord.File(
        fp=buffer,
        filename=(
            f"ticket-{ticket_number:04d}.html"
        )
    )

async def send_ticket_log(
    guild: discord.Guild,
    embed: discord.Embed
):

    log_channel = guild.get_channel(
        TICKET_LOG_CHANNEL_ID
    )

    if not isinstance(
        log_channel,
        discord.TextChannel
    ):
        return

    await log_channel.send(
        embed=embed,
        allowed_mentions=
            discord.AllowedMentions.none()
    )

async def close_ticket(
    interaction: discord.Interaction
):

    if not isinstance(
        interaction.user,
        discord.Member
    ):
        return

    if not is_staff(
        interaction.user
    ):
        await interaction.response.send_message(
            "Only staff can close tickets.",
            ephemeral=True
        )

        return

    if not isinstance(
        interaction.channel,
        discord.TextChannel
    ):
        return

    ticket_row = get_ticket_by_channel(
        interaction.channel.id
    )

    if ticket_row is None:
        await interaction.response.send_message(
            "This channel is not registered as a ticket.",
            ephemeral=True
        )

        return

    if ticket_row["status"] != "open":

        await interaction.response.send_message(
            "This ticket is already closed.",
            ephemeral=True
        )

        return

    await interaction.response.defer(
        ephemeral=True
    )

    transcript_message_id = None

    transcript_channel = (
        interaction.guild.get_channel(
            TRANSCRIPT_CHANNEL_ID
        )
        if interaction.guild
        else None
    )

    try:

        transcript_file = (
            await generate_html_transcript(
                interaction.channel,
                ticket_row
            )
        )

        if isinstance(
            transcript_channel,
            discord.TextChannel
        ):

            transcript_embed = discord.Embed(
                title="📄 Ticket Transcript",
                color=discord.Color.from_rgb(
                    224,
                    0,
                    0
                )
            )

            transcript_embed.add_field(
                name="Ticket",
                value=(
                    f"`#{int(ticket_row['ticket_number']):04d}`"
                ),
                inline=True
            )

            transcript_embed.add_field(
                name="Type",
                value=(
                    ticket_row["ticket_type"]
                ),
                inline=True
            )

            transcript_embed.add_field(
                name="Creator",
                value=(
                    f"<@{ticket_row['creator_id']}>"
                ),
                inline=False
            )

            transcript_embed.add_field(
                name="Closed By",
                value=(
                    interaction.user.mention
                ),
                inline=False
            )

            transcript_message = (
                await transcript_channel.send(
                    embed=transcript_embed,
                    file=transcript_file,
                    allowed_mentions=
                        discord.AllowedMentions.none()
                )
            )

            transcript_message_id = (
                transcript_message.id
            )

    except Exception as ex:

        print(
            f"Transcript generation failed: {ex}"
        )

    now = datetime.now(
        timezone.utc
    ).isoformat()

    update_data = {
        "status": "closed",
        "closed_at": now,
        "closed_by": str(
            interaction.user.id
        )
    }

    if transcript_message_id is not None:

        update_data[
            "transcript_message_id"
        ] = str(
            transcript_message_id
        )

    try:

        (
            supabase
            .table("tickets")
            .update(
                update_data
            )
            .eq(
                "id",
                ticket_row["id"]
            )
            .execute()
        )

    except Exception as ex:

        print(
            f"Failed to update closed ticket: {ex}"
        )

    creator_id = int(
        ticket_row["creator_id"]
    )

    creator = (
        interaction.guild.get_member(
            creator_id
        )
        if interaction.guild
        else None
    )

    if creator is not None:

        try:

            await interaction.channel.set_permissions(
                creator,
                view_channel=True,
                send_messages=False,
                read_message_history=True,
                attach_files=False
            )

        except Exception as ex:

            print(
                f"Failed to lock ticket creator: {ex}"
            )

    closed_embed = discord.Embed(
        title="🔒 Ticket Closed",
        description=(
            f"This ticket was closed by "
            f"{interaction.user.mention}.\n\n"
            f"Staff may reopen or delete the ticket "
            f"using the controls below."
        ),
        color=discord.Color.dark_red()
    )

    await interaction.channel.send(
        embed=closed_embed,
        view=ClosedTicketControlsView(),
        allowed_mentions=
            discord.AllowedMentions.none()
    )

    if interaction.guild is not None:

        log_embed = discord.Embed(
            title="🔒 Ticket Closed",
            color=discord.Color.dark_red()
        )

        log_embed.add_field(
            name="Ticket",
            value=(
                f"`#{int(ticket_row['ticket_number']):04d}`"
            ),
            inline=True
        )

        log_embed.add_field(
            name="Channel",
            value=interaction.channel.mention,
            inline=True
        )

        log_embed.add_field(
            name="Creator",
            value=(
                f"<@{ticket_row['creator_id']}>\n"
                f"`{ticket_row['creator_id']}`"
            ),
            inline=False
        )

        log_embed.add_field(
            name="Closed By",
            value=(
                f"{interaction.user.mention}\n"
                f"`{interaction.user.id}`"
            ),
            inline=False
        )

        await send_ticket_log(
            interaction.guild,
            log_embed
        )

    await interaction.followup.send(
        "Ticket closed successfully.",
        ephemeral=True
    )

async def reopen_ticket(
    interaction: discord.Interaction
):

    if not isinstance(
        interaction.user,
        discord.Member
    ):
        return

    if not is_staff(
        interaction.user
    ):

        await interaction.response.send_message(
            "Only staff can reopen tickets.",
            ephemeral=True
        )

        return

    if not isinstance(
        interaction.channel,
        discord.TextChannel
    ):
        return

    ticket_row = get_ticket_by_channel(
        interaction.channel.id
    )

    if ticket_row is None:

        await interaction.response.send_message(
            "This channel is not registered as a ticket.",
            ephemeral=True
        )

        return

    if ticket_row["status"] != "closed":

        await interaction.response.send_message(
            "This ticket is already open.",
            ephemeral=True
        )

        return

    creator_id = int(
        ticket_row["creator_id"]
    )

    try:

        if await user_has_other_open_ticket(
            creator_id,
            int(
                ticket_row["id"]
            )
        ):

            await interaction.response.send_message(
                (
                    "This user already has another open ticket. "
                    "Close that ticket before reopening this one."
                ),
                ephemeral=True
            )

            return

    except Exception as ex:

        print(
            f"Reopen ticket check failed: {ex}"
        )

        await interaction.response.send_message(
            "The ticket database could not be reached.",
            ephemeral=True
        )

        return

    await interaction.response.defer(
        ephemeral=True
    )

    creator = (
        interaction.guild.get_member(
            creator_id
        )
        if interaction.guild
        else None
    )

    if creator is not None:

        try:

            await interaction.channel.set_permissions(
                creator,
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                attach_files=True,
                embed_links=True
            )

        except Exception as ex:

            print(
                f"Failed to restore ticket creator: {ex}"
            )

    try:

        (
            supabase
            .table("tickets")
            .update(
                {
                    "status": "open",
                    "closed_at": None,
                    "closed_by": None
                }
            )
            .eq(
                "id",
                ticket_row["id"]
            )
            .execute()
        )

    except Exception as ex:

        print(
            f"Failed to reopen ticket in database: {ex}"
        )

    reopen_embed = discord.Embed(
        title="🔓 Ticket Reopened",
        description=(
            f"This ticket was reopened by "
            f"{interaction.user.mention}."
        ),
        color=discord.Color.green()
    )

    await interaction.channel.send(
        embed=reopen_embed,
        view=OpenTicketControlsView(),
        allowed_mentions=
            discord.AllowedMentions.none()
    )

    if interaction.guild is not None:

        log_embed = discord.Embed(
            title="🔓 Ticket Reopened",
            color=discord.Color.green()
        )

        log_embed.add_field(
            name="Ticket",
            value=(
                f"`#{int(ticket_row['ticket_number']):04d}`"
            ),
            inline=True
        )

        log_embed.add_field(
            name="Channel",
            value=interaction.channel.mention,
            inline=True
        )

        log_embed.add_field(
            name="Reopened By",
            value=(
                f"{interaction.user.mention}\n"
                f"`{interaction.user.id}`"
            ),
            inline=False
        )

        await send_ticket_log(
            interaction.guild,
            log_embed
        )

    await interaction.followup.send(
        "Ticket reopened successfully.",
        ephemeral=True
    )

async def delete_ticket(
    interaction: discord.Interaction
):

    if not isinstance(
        interaction.user,
        discord.Member
    ):
        return


    if not is_staff(
        interaction.user
    ):

        await interaction.response.send_message(
            "Only staff can delete tickets.",
            ephemeral=True
        )

        return

    if not isinstance(
        interaction.channel,
        discord.TextChannel
    ):
        return

    ticket_row = get_ticket_by_channel(
        interaction.channel.id
    )

    if ticket_row is None:

        await interaction.response.send_message(
            "This channel is not registered as a ticket.",
            ephemeral=True
        )

        return

    if ticket_row["status"] != "closed":

        await interaction.response.send_message(
            "You must close the ticket before deleting it.",
            ephemeral=True
        )

        return

    await interaction.response.send_message(
        "Deleting ticket in 3 seconds...",
        ephemeral=True
    )

    if interaction.guild is not None:

        log_embed = discord.Embed(
            title="🗑️ Ticket Deleted",
            color=discord.Color.dark_grey()
        )

        log_embed.add_field(
            name="Ticket",
            value=(
                f"`#{int(ticket_row['ticket_number']):04d}`"
            ),
            inline=True
        )

        log_embed.add_field(
            name="Channel",
            value=interaction.channel.name,
            inline=True
        )

        log_embed.add_field(
            name="Deleted By",
            value=(
                f"{interaction.user.mention}\n"
                f"`{interaction.user.id}`"
            ),
            inline=False
        )

        await send_ticket_log(
            interaction.guild,
            log_embed
        )

    import asyncio

    await asyncio.sleep(
        3
    )

    try:

        await interaction.channel.delete(
            reason=(
                f"Ticket deleted by "
                f"{interaction.user}"
            )
        )

    except Exception as ex:

        print(
            f"Failed to delete ticket channel: {ex}"
        )

class OpenTicketControlsView(
    discord.ui.View
):

    def __init__(
        self
    ):
        super().__init__(
            timeout=None
        )

    @discord.ui.button(
        label="Close Ticket",
        style=discord.ButtonStyle.danger,
        emoji="🔒",
        custom_id="daboyz_ticket_close"
    )
    async def close_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await close_ticket(
            interaction
        )

class ClosedTicketControlsView(
    discord.ui.View
):

    def __init__(
        self
    ):
        super().__init__(
            timeout=None
        )

    @discord.ui.button(
        label="Reopen",
        style=discord.ButtonStyle.success,
        emoji="🔓",
        custom_id="daboyz_ticket_reopen"
    )
    async def reopen_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await reopen_ticket(
            interaction
        )

    @discord.ui.button(
        label="Delete",
        style=discord.ButtonStyle.danger,
        emoji="🗑️",
        custom_id="daboyz_ticket_delete"
    )
    async def delete_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await delete_ticket(
            interaction
        )

async def create_ticket(
    interaction: discord.Interaction,
    ticket_type: str,
    ticket_label: str,
    answers: list[tuple[str, str]]
):

    guild = interaction.guild

    if guild is None:

        await interaction.response.send_message(
            (
                "This ticket system can only be used "
                "inside the Da Boyz server."
            ),
            ephemeral=True
        )

        return

    try:

        if await user_has_open_ticket(
            interaction.user.id
        ):

            await interaction.response.send_message(
                "You already have an open ticket.",
                ephemeral=True
            )

            return

    except Exception as ex:

        print(
            f"Ticket database check failed: {ex}"
        )

        await interaction.response.send_message(
            (
                "The ticket database could not be reached. "
                "Please try again."
            ),
            ephemeral=True
        )

        return

    await interaction.response.defer(
        ephemeral=True
    )

    try:

        insert_response = (
            supabase
            .table("tickets")
            .insert(
                {
                    "guild_id":
                        str(GUILD_ID),

                    "creator_id":
                        str(
                            interaction.user.id
                        ),

                    "ticket_type":
                        ticket_type,

                    "status":
                        "open"
                }
            )
            .execute()
        )

        if not insert_response.data:

            raise RuntimeError(
                "Supabase returned no ticket row."
            )

        ticket_row = (
            insert_response.data[0]
        )

        ticket_id = (
            ticket_row["id"]
        )

        ticket_number = int(
            ticket_row["ticket_number"]
        )

    except Exception as ex:

        print(
            f"Ticket row creation failed: {ex}"
        )

        await interaction.followup.send(
            (
                "The ticket could not be created because "
                "the database request failed."
            ),
            ephemeral=True
        )

        return

    ticket_name = (
        f"ticket-{ticket_number:04d}"
    )

    category = guild.get_channel(
        TICKET_CATEGORY_ID
    )

    if not isinstance(
        category,
        discord.CategoryChannel
    ):

        await interaction.followup.send(
            (
                "The configured ticket category "
                "could not be found."
            ),
            ephemeral=True
        )

        try:

            (
                supabase
                .table("tickets")
                .delete()
                .eq(
                    "id",
                    ticket_id
                )
                .execute()
            )

        except Exception:
            pass

        return

    overwrites = {

        guild.default_role:

            discord.PermissionOverwrite(
                view_channel=False
            ),

        interaction.user:

            discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                attach_files=True,
                embed_links=True
            )
    }

    if guild.me is not None:

        overwrites[
            guild.me
        ] = discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            read_message_history=True,
            manage_channels=True,
            manage_messages=True,
            attach_files=True,
            embed_links=True
        )

    for role_id in STAFF_ROLE_IDS:

        role = guild.get_role(
            role_id
        )

        if role is None:
            continue

        overwrites[
            role
        ] = discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            read_message_history=True,
            attach_files=True,
            embed_links=True
        )

    try:

        ticket_channel = (
            await guild.create_text_channel(
                name=ticket_name,
                category=category,
                overwrites=overwrites,

                topic=(
                    f"Da Boyz Ticket | "
                    f"Ticket #{ticket_number:04d} | "
                    f"Creator: {interaction.user.id} | "
                    f"Type: {ticket_type}"
                ),

                reason=(
                    f"Ticket created by "
                    f"{interaction.user}"
                )
            )
        )

    except Exception as ex:

        print(
            f"Discord ticket channel creation failed: {ex}"
        )

        try:

            (
                supabase
                .table("tickets")
                .delete()
                .eq(
                    "id",
                    ticket_id
                )
                .execute()
            )

        except Exception:
            pass

        await interaction.followup.send(
            (
                "I couldn't create the ticket channel. "
                "Check my channel permissions."
            ),
            ephemeral=True
        )

        return

    try:

        (
            supabase
            .table("tickets")
            .update(
                {
                    "channel_id":
                        str(
                            ticket_channel.id
                        )
                }
            )
            .eq(
                "id",
                ticket_id
            )
            .execute()
        )

    except Exception as ex:

        print(
            f"Failed to save ticket channel ID: {ex}"
        )

    embed = discord.Embed(
        title=(
            f"🎫 {ticket_label}"
        ),

        description=(
            f"Welcome {interaction.user.mention}.\n\n"
            f"A member of the Da Boyz staff team will "
            f"assist you as soon as possible."
        ),

        color=discord.Color.from_rgb(
            224,
            0,
            0
        )
    )

    embed.add_field(
        name="Ticket",
        value=(
            f"`#{ticket_number:04d}`"
        ),
        inline=True
    )

    embed.add_field(
        name="Opened By",
        value=(
            interaction.user.mention
        ),
        inline=True
    )

    embed.add_field(
        name="Type",
        value=ticket_label,
        inline=True
    )

    for question, answer in answers:

        cleaned_answer = (
            answer.strip()
            if answer.strip()
            else "No answer provided."
        )

        embed.add_field(
            name=question,
            value=cleaned_answer,
            inline=False
        )

    embed.set_footer(
        text="Da Boyz Ticket System"
    )

    await ticket_channel.send(
        content=(
            f"{interaction.user.mention} "
            f"<@&{STAFF_ROLE_ID}>"
        ),

        embed=embed,

        view=OpenTicketControlsView(),

        allowed_mentions=
            discord.AllowedMentions(
                users=True,
                roles=True,
                everyone=False
            )
    )

    log_embed = discord.Embed(
        title="🎫 Ticket Opened",
        color=discord.Color.from_rgb(
            224,
            0,
            0
        )
    )

    log_embed.add_field(
        name="Ticket",
        value=(
            f"`#{ticket_number:04d}`"
        ),
        inline=True
    )

    log_embed.add_field(
        name="Type",
        value=ticket_label,
        inline=True
    )

    log_embed.add_field(
        name="User",
        value=(
            f"{interaction.user.mention}\n"
            f"`{interaction.user.id}`"
        ),
        inline=False
    )

    log_embed.add_field(
        name="Channel",
        value=(
            ticket_channel.mention
        ),
        inline=False
    )

    await send_ticket_log(
        guild,
        log_embed
    )

    await interaction.followup.send(
        (
            "Your ticket has been created: "
            f"{ticket_channel.mention}"
        ),
        ephemeral=True
    )

class SupportModal(
    discord.ui.Modal,
    title="Da Boyz Support"
):

    username = discord.ui.TextInput(
        label="What is your Discord username?",
        required=True,
        max_length=100
    )

    issue = discord.ui.TextInput(
        label="What issue are you having?",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=1000
    )

    escalation = discord.ui.TextInput(
        label="Escalate to management?",
        placeholder="Yes / No",
        required=True,
        max_length=50
    )

    evidence = discord.ui.TextInput(
        label="Do you have screenshots/clips?",
        placeholder="Paste links here, or type No",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=1000
    )

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        await create_ticket(
            interaction=interaction,
            ticket_type="support",
            ticket_label="Support",

            answers=[
                (
                    "Discord Username",
                    str(
                        self.username
                    )
                ),

                (
                    "Issue",
                    str(
                        self.issue
                    )
                ),

                (
                    "Escalate to Management?",
                    str(
                        self.escalation
                    )
                ),

                (
                    "Screenshots / Clips",
                    str(
                        self.evidence
                    )
                )
            ]
        )

class MemberReportModal(
    discord.ui.Modal,
    title="Member Report"
):

    username = discord.ui.TextInput(
        label="What is your Discord username?",
        required=True,
        max_length=100
    )

    reported_user = discord.ui.TextInput(
        label="Who are you reporting?",
        required=True,
        max_length=100
    )

    reason = discord.ui.TextInput(
        label="Reason for reporting?",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=1000
    )

    evidence = discord.ui.TextInput(
        label="Do you have screenshots/clips?",
        placeholder="Paste links here, or type No",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=1000
    )

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        await create_ticket(
            interaction=interaction,
            ticket_type="member_report",
            ticket_label="Member Report",

            answers=[
                (
                    "Discord Username",
                    str(
                        self.username
                    )
                ),

                (
                    "Reported Member",
                    str(
                        self.reported_user
                    )
                ),

                (
                    "Reason",
                    str(
                        self.reason
                    )
                ),

                (
                    "Screenshots / Clips",
                    str(
                        self.evidence
                    )
                )
            ]
        )

class StaffApplicationModal(
    discord.ui.Modal,
    title="Staff Application"
):

    username = discord.ui.TextInput(
        label="What is your Discord username?",
        required=True,
        max_length=100
    )

    about = discord.ui.TextInput(
        label="Tell us about yourself.",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=1000
    )

    admin_experience = discord.ui.TextInput(
        label="Previous admin/mod experience?",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=1000
    )

    discord_experience = discord.ui.TextInput(
        label="What Discord experience do you have?",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=1000
    )

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        await create_ticket(
            interaction=interaction,
            ticket_type="staff_application",
            ticket_label="Staff Application",

            answers=[
                (
                    "Discord Username",
                    str(
                        self.username
                    )
                ),

                (
                    "About",
                    str(
                        self.about
                    )
                ),

                (
                    "Admin / Moderator Experience",
                    str(
                        self.admin_experience
                    )
                ),

                (
                    "Discord Experience",
                    str(
                        self.discord_experience
                    )
                )
            ]
        )

class TicketPanelView(
    discord.ui.View
):

    def __init__(
        self
    ):
        super().__init__(
            timeout=None
        )

    @discord.ui.button(
        label="Support",
        style=discord.ButtonStyle.primary,
        emoji="🛠️",
        custom_id="daboyz_ticket_support"
    )
    async def support(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.send_modal(
            SupportModal()
        )

    @discord.ui.button(
        label="Member Report",
        style=discord.ButtonStyle.danger,
        emoji="⚠️",
        custom_id="daboyz_ticket_member_report"
    )
    async def member_report(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.send_modal(
            MemberReportModal()
        )

    @discord.ui.button(
        label="Staff Application",
        style=discord.ButtonStyle.success,
        emoji="📋",
        custom_id="daboyz_ticket_staff_application"
    )
    async def staff_application(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.send_modal(
            StaffApplicationModal()
        )

class Tickets(
    commands.Cog
):

    def __init__(
        self,
        bot: commands.Bot
    ):

        self.bot = bot

    @discord.app_commands.command(
        name="ticket-panel",
        description="Creates the Da Boyz ticket panel."
    )
    @discord.app_commands.guilds(
        discord.Object(
            id=GUILD_ID
        )
    )
    async def ticket_panel(
        self,
        interaction: discord.Interaction
    ):

        if not isinstance(
            interaction.user,
            discord.Member
        ):

            return

        has_staff_role = any(
            role.id in STAFF_ROLE_IDS
            for role in interaction.user.roles
        )

        if (
            not interaction.user.guild_permissions.administrator
            and not has_staff_role
        ):

            await interaction.response.send_message(
                (
                    "You do not have permission to "
                    "create the ticket panel."
                ),
                ephemeral=True
            )

            return

        guild = interaction.guild

        if guild is None:
            return

        panel_channel = guild.get_channel(
            TICKET_PANEL_CHANNEL_ID
        )

        if not isinstance(
            panel_channel,
            discord.TextChannel
        ):

            await interaction.response.send_message(
                (
                    "The configured ticket panel "
                    "channel could not be found."
                ),
                ephemeral=True
            )

            return

        embed = discord.Embed(
            title="🎫 Da Boyz Support",

            description=(
                "Need assistance? Open a ticket below.\n\n"

                "**Support**\n"
                "General help or server-related issues.\n\n"

                "**Member Report**\n"
                "Report another community member to staff.\n\n"

                "**Staff Application**\n"
                "Apply to become a member of the "
                "Da Boyz staff team.\n\n"

                "Please only open a ticket when necessary. "
                "You may only have **one open ticket at a time**."
            ),

            color=discord.Color.from_rgb(
                224,
                0,
                0
            )
        )

        embed.set_footer(
            text="Da Boyz Ticket System"
        )

        await panel_channel.send(
            embed=embed,
            view=TicketPanelView()
        )

        await interaction.response.send_message(
            (
                "Ticket panel successfully created in "
                f"{panel_channel.mention}."
            ),
            ephemeral=True
        )

async def setup(
    bot: commands.Bot
):

    bot.add_view(
        TicketPanelView()
    )

    bot.add_view(
        OpenTicketControlsView()
    )

    bot.add_view(
        ClosedTicketControlsView()
    )

    await bot.add_cog(
        Tickets(bot)
    )