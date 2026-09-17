# KaroDevGroup
# Josh Karo

import re
import discord
from discord.ext import commands


GUILD_ID = 908868924488171540

MESSAGE_LINK_PATTERN = re.compile(
    r"https?://(?:canary\.|ptb\.)?discord(?:app)?\.com/"
    r"channels/(\d+)/(\d+)/(\d+)"
)

def parse_message_link(message_link: str):
    match = MESSAGE_LINK_PATTERN.fullmatch(
        message_link.strip()
    )

    if not match:
        return None

    guild_id = int(match.group(1))
    channel_id = int(match.group(2))
    message_id = int(match.group(3))

    return guild_id, channel_id, message_id

class EmbedPreviewView(discord.ui.View):
    def __init__(
        self,
        target_channel: discord.TextChannel,
        embed: discord.Embed,
        creator_id: int
    ):
        super().__init__(
            timeout=300
        )

        self.target_channel = target_channel
        self.embed = embed
        self.creator_id = creator_id

    async def interaction_check(
        self,
        interaction: discord.Interaction
    ) -> bool:

        if interaction.user.id != self.creator_id:
            await interaction.response.send_message(
                "Only the person who created this embed "
                "can use these controls.",
                ephemeral=True
            )

            return False

        return True

    @discord.ui.button(
        label="Send Embed",
        style=discord.ButtonStyle.success,
        emoji="✅"
    )
    async def send_embed(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        try:
            message = await self.target_channel.send(
                embed=self.embed,
                allowed_mentions=
                    discord.AllowedMentions.none()
            )

        except discord.Forbidden:
            await interaction.response.edit_message(
                content=(
                    "❌ I do not have permission to send "
                    f"messages in {self.target_channel.mention}."
                ),
                embed=None,
                view=None
            )

            return

        except discord.HTTPException as ex:
            await interaction.response.edit_message(
                content=f"❌ Discord rejected the embed: `{ex}`",
                embed=None,
                view=None
            )

            return

        for item in self.children:
            item.disabled = True

        await interaction.response.edit_message(
            content=(
                f"✅ Embed sent successfully to "
                f"{self.target_channel.mention}.\n\n"
                f"[Jump to message]({message.jump_url})"
            ),
            embed=self.embed,
            view=self
        )

        self.stop()

    @discord.ui.button(
        label="Cancel",
        style=discord.ButtonStyle.danger,
        emoji="✖️"
    )
    async def cancel_embed(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.edit_message(
            content="Embed creation cancelled.",
            embed=None,
            view=None
        )

        self.stop()

class EmbedModal(discord.ui.Modal):
    def __init__(
        self,
        target_channel: discord.TextChannel
    ):
        super().__init__(
            title="Da Boyz Embed Builder"
        )

        self.target_channel = target_channel

        self.embed_title = discord.ui.TextInput(
            label="Title",
            placeholder="UPDATED Server Rules:",
            required=True,
            max_length=256
        )

        self.embed_description = discord.ui.TextInput(
            label="Description",
            placeholder="Enter the main embed content here...",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=4000
        )

        self.embed_color = discord.ui.TextInput(
            label="Color",
            placeholder="E00000",
            default="E00000",
            required=False,
            max_length=7
        )

        self.thumbnail_url = discord.ui.TextInput(
            label="Thumbnail URL",
            placeholder="https://example.com/image.png",
            required=False
        )

        self.image_url = discord.ui.TextInput(
            label="Large Image / Banner URL",
            placeholder="https://example.com/banner.png",
            required=False
        )

        self.add_item(
            self.embed_title
        )

        self.add_item(
            self.embed_description
        )

        self.add_item(
            self.embed_color
        )

        self.add_item(
            self.thumbnail_url
        )

        self.add_item(
            self.image_url
        )

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):
        color_text = (
            str(self.embed_color.value)
            .replace("#", "")
            .strip()
        )

        if not color_text:
            color_text = "E00000"

        try:
            color_value = int(
                color_text,
                16
            )

            if color_value < 0 or color_value > 0xFFFFFF:
                raise ValueError

            embed_color = discord.Color(
                color_value
            )

        except ValueError:
            await interaction.response.send_message(
                "Invalid color. Use a hex value such as "
                "`E00000` or `#E00000`.",
                ephemeral=True
            )

            return

        embed = discord.Embed(
            title=str(
                self.embed_title.value
            ),
            description=str(
                self.embed_description.value
            ),
            color=embed_color
        )

        thumbnail = str(
            self.thumbnail_url.value
        ).strip()

        if thumbnail:
            embed.set_thumbnail(
                url=thumbnail
            )

        image = str(
            self.image_url.value
        ).strip()

        if image:
            embed.set_image(
                url=image
            )

        preview_view = EmbedPreviewView(
            target_channel=self.target_channel,
            embed=embed,
            creator_id=interaction.user.id
        )

        await interaction.response.send_message(
            content=(
                f"### Embed Preview\n"
                f"Target: {self.target_channel.mention}\n\n"
                f"Review the embed below before sending."
            ),
            embed=embed,
            view=preview_view,
            ephemeral=True
        )

class EditEmbedPreviewView(discord.ui.View):
    def __init__(
        self,
        target_message: discord.Message,
        embed: discord.Embed,
        creator_id: int
    ):
        super().__init__(
            timeout=300
        )

        self.target_message = target_message
        self.embed = embed
        self.creator_id = creator_id

    async def interaction_check(
        self,
        interaction: discord.Interaction
    ) -> bool:

        if interaction.user.id != self.creator_id:
            await interaction.response.send_message(
                "Only the person editing this embed "
                "can use these controls.",
                ephemeral=True
            )

            return False

        return True

    @discord.ui.button(
        label="Save Changes",
        style=discord.ButtonStyle.success,
        emoji="💾"
    )
    async def save_changes(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        try:
            await self.target_message.edit(
                embed=self.embed
            )

        except discord.Forbidden:
            await interaction.response.edit_message(
                content=(
                    "❌ I do not have permission to edit "
                    "that message."
                ),
                embed=None,
                view=None
            )

            return

        except discord.HTTPException as ex:
            await interaction.response.edit_message(
                content=(
                    f"❌ Discord rejected the edit: `{ex}`"
                ),
                embed=None,
                view=None
            )

            return

        for item in self.children:
            item.disabled = True

        await interaction.response.edit_message(
            content=(
                "✅ Embed updated successfully.\n\n"
                f"[Jump to message]"
                f"({self.target_message.jump_url})"
            ),
            embed=self.embed,
            view=self
        )

        self.stop()

    @discord.ui.button(
        label="Cancel",
        style=discord.ButtonStyle.danger,
        emoji="✖️"
    )
    async def cancel_edit(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.edit_message(
            content=(
                "Embed edit cancelled. "
                "The original message was not changed."
            ),
            embed=None,
            view=None
        )

        self.stop()

class EditEmbedModal(discord.ui.Modal):
    def __init__(
        self,
        target_message: discord.Message,
        existing_embed: discord.Embed
    ):
        super().__init__(
            title="Edit Da Boyz Embed"
        )

        self.target_message = target_message

        current_title = (
            existing_embed.title
            or ""
        )

        current_description = (
            existing_embed.description
            or ""
        )

        current_color = "E00000"

        if existing_embed.color:
            current_color = (
                f"{existing_embed.color.value:06X}"
            )

        current_thumbnail = ""

        if (
            existing_embed.thumbnail
            and existing_embed.thumbnail.url
        ):
            current_thumbnail = (
                existing_embed.thumbnail.url
            )

        current_image = ""

        if (
            existing_embed.image
            and existing_embed.image.url
        ):
            current_image = (
                existing_embed.image.url
            )

        self.embed_title = discord.ui.TextInput(
            label="Title",
            default=current_title,
            required=True,
            max_length=256
        )

        self.embed_description = discord.ui.TextInput(
            label="Description",
            default=current_description,
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=4000
        )

        self.embed_color = discord.ui.TextInput(
            label="Color",
            default=current_color,
            required=False,
            max_length=7
        )

        self.thumbnail_url = discord.ui.TextInput(
            label="Thumbnail URL",
            default=current_thumbnail,
            required=False
        )

        self.image_url = discord.ui.TextInput(
            label="Large Image / Banner URL",
            default=current_image,
            required=False
        )

        self.add_item(
            self.embed_title
        )

        self.add_item(
            self.embed_description
        )

        self.add_item(
            self.embed_color
        )

        self.add_item(
            self.thumbnail_url
        )

        self.add_item(
            self.image_url
        )

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):
        color_text = (
            str(self.embed_color.value)
            .replace("#", "")
            .strip()
        )

        if not color_text:
            color_text = "E00000"

        try:
            color_value = int(
                color_text,
                16
            )

            if color_value < 0 or color_value > 0xFFFFFF:
                raise ValueError

            embed_color = discord.Color(
                color_value
            )

        except ValueError:
            await interaction.response.send_message(
                "Invalid color. Use a hex value such as "
                "`E00000` or `#E00000`.",
                ephemeral=True
            )

            return

        updated_embed = discord.Embed(
            title=str(
                self.embed_title.value
            ),
            description=str(
                self.embed_description.value
            ),
            color=embed_color
        )

        thumbnail = str(
            self.thumbnail_url.value
        ).strip()

        if thumbnail:
            updated_embed.set_thumbnail(
                url=thumbnail
            )

        image = str(
            self.image_url.value
        ).strip()

        if image:
            updated_embed.set_image(
                url=image
            )

        preview_view = EditEmbedPreviewView(
            target_message=self.target_message,
            embed=updated_embed,
            creator_id=interaction.user.id
        )

        await interaction.response.send_message(
            content=(
                "### Updated Embed Preview\n"
                "Review your changes before saving.\n\n"
                f"[View Original Message]"
                f"({self.target_message.jump_url})"
            ),
            embed=updated_embed,
            view=preview_view,
            ephemeral=True
        )

class EmbedCommand(commands.Cog):
    def __init__(
        self,
        bot: commands.Bot
    ):
        self.bot = bot

    @discord.app_commands.command(
        name="create-embed",
        description="Creates a custom Discord embed."
    )
    @discord.app_commands.guilds(
        discord.Object(
            id=GUILD_ID
        )
    )
    @discord.app_commands.describe(
        channel="Channel where the embed should be sent"
    )
    async def create_embed(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel
    ):
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message(
                "You do not have permission to use this command.",
                ephemeral=True
            )

            return

        modal = EmbedModal(
            target_channel=channel
        )

        await interaction.response.send_modal(
            modal
        )

    @discord.app_commands.command(
        name="edit-embed",
        description="Edits an existing DaBoyzBot embed."
    )
    @discord.app_commands.guilds(
        discord.Object(
            id=GUILD_ID
        )
    )
    @discord.app_commands.describe(
        message_link=(
            "Discord message link for the embed "
            "you want to edit"
        )
    )
    async def edit_embed(
        self,
        interaction: discord.Interaction,
        message_link: str
    ):

        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message(
                "You do not have permission to use this command.",
                ephemeral=True
            )

            return

        parsed = parse_message_link(
            message_link
        )

        if parsed is None:
            await interaction.response.send_message(
                "That does not look like a valid Discord message link.",
                ephemeral=True
            )

            return

        guild_id, channel_id, message_id = parsed

        if guild_id != GUILD_ID:
            await interaction.response.send_message(
                "That message is not from the Da Boyz server.",
                ephemeral=True
            )

            return

        channel = self.bot.get_channel(
            channel_id
        )

        if channel is None:
            try:
                channel = await self.bot.fetch_channel(
                    channel_id
                )

            except discord.HTTPException:
                await interaction.response.send_message(
                    "I could not access the channel "
                    "from that message link.",
                    ephemeral=True
                )

                return

        try:
            message = await channel.fetch_message(
                message_id
            )

        except discord.NotFound:
            await interaction.response.send_message(
                "I could not find that message.",
                ephemeral=True
            )

            return

        except discord.Forbidden:
            await interaction.response.send_message(
                "I do not have permission to access "
                "that message.",
                ephemeral=True
            )

            return

        except discord.HTTPException as ex:
            await interaction.response.send_message(
                f"Failed to load the message: `{ex}`",
                ephemeral=True
            )

            return

        if self.bot.user is None:
            await interaction.response.send_message(
                "Bot user information is unavailable.",
                ephemeral=True
            )

            return

        if message.author.id != self.bot.user.id:
            await interaction.response.send_message(
                (
                    "I can only edit embeds that were "
                    "originally sent by DaBoyzBot."
                ),
                ephemeral=True
            )

            return

        if not message.embeds:
            await interaction.response.send_message(
                "That message does not contain an embed.",
                ephemeral=True
            )

            return

        existing_embed = message.embeds[0]

        modal = EditEmbedModal(
            target_message=message,
            existing_embed=existing_embed
        )


        await interaction.response.send_modal(
            modal
        )

async def setup(
    bot: commands.Bot
):
    await bot.add_cog(
        EmbedCommand(bot)
    )