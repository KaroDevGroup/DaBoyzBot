# KaroDevGroup
# Josh Karo

import asyncio
from datetime import datetime, timezone
import discord
from discord.ext import commands, tasks
from supabase_client import supabase


class ModerationBridge(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.process_requests.start()

    def cog_unload(self):
        self.process_requests.cancel()

    @tasks.loop(seconds=5)
    async def process_requests(self):
        try:
            response = await asyncio.to_thread(
                lambda: (
                    supabase
                    .table("moderation_requests")
                    .select("*")
                    .eq("status", "pending")
                    .order("created_at")
                    .limit(10)
                    .execute()
                )
            )

            requests = response.data or []

            for request in requests:
                await self.process_request(
                    request
                )

        except Exception as error:
            print(
                "[Moderation Bridge] "
                f"Failed to read requests: {error}"
            )

    @process_requests.before_loop
    async def before_process_requests(self):
        await self.bot.wait_until_ready()

    async def process_request(
        self,
        request: dict
    ):
        request_id = request.get("id")
        action = request.get("action")

        if not request_id:
            return

        try:
            claim_response = await asyncio.to_thread(
                lambda: (
                    supabase
                    .table("moderation_requests")
                    .update({
                        "status": "processing"
                    })
                    .eq("id", request_id)
                    .eq("status", "pending")
                    .execute()
                )
            )

            if not claim_response.data:
                return

        except Exception as error:
            print(
                "[Moderation Bridge] "
                f"Could not claim request {request_id}: "
                f"{error}"
            )
            return

        try:
            if action == "warn":
                await self.process_warn(
                    request
                )

            elif action == "timeout":
                await self.process_timeout(
                    request
                )

            elif action == "kick":
                await self.process_kick(
                    request
                )

            elif action == "ban": 
                await self.process_ban(
                    request
                )

            elif action == "unban":
                await self.process_unban(
                    request
                )

            elif action == "clear":
                await self.process_clear(
                    request
                )

            elif action == "lock":
                await self.process_lock(
                    request
                )

            elif action == "unlock":
                await self.process_unlock(
                    request
                )

            else:
                await self.mark_failed(
                    request_id,
                    f"Unsupported moderation action: {action}"
                )

        except Exception as error:
            await self.mark_failed(
                request_id,
                str(error)
            )

    async def process_warn(
        self,
        request: dict
    ):
        request_id = request["id"]

        guild_id = self.parse_id(
            request.get("guild_id")
        )

        moderator_id = self.parse_id(
            request.get("moderator_id")
        )

        target_user_id = self.parse_id(
            request.get("target_user_id")
        )

        reason = (
            request.get("reason")
            or "No reason provided"
        )

        if guild_id is None:
            await self.mark_failed(
                request_id,
                "Invalid guild ID."
            )
            return

        if moderator_id is None:
            await self.mark_failed(
                request_id,
                "Invalid moderator ID."
            )
            return

        if target_user_id is None:
            await self.mark_failed(
                request_id,
                "Invalid target user ID."
            )
            return

        guild = self.bot.get_guild(
            guild_id
        )

        if guild is None:
            await self.mark_failed(
                request_id,
                "Discord server could not be found."
            )
            return

        moderator = guild.get_member(
            moderator_id
        )

        if moderator is None:
            try:
                moderator = await guild.fetch_member(
                    moderator_id
                )
            except discord.NotFound:
                moderator = None
            except discord.HTTPException:
                moderator = None

        if moderator is None:
            await self.mark_failed(
                request_id,
                "Moderator could not be found in the server."
            )
            return

        member = guild.get_member(
            target_user_id
        )

        if member is None:
            try:
                member = await guild.fetch_member(
                    target_user_id
                )
            except discord.NotFound:
                member = None
            except discord.HTTPException:
                member = None

        if member is None:
            await self.mark_failed(
                request_id,
                "Target member could not be found in the server."
            )
            return

        warn_cog = self.bot.get_cog(
            "Warn"
        )

        if warn_cog is None:
            await self.mark_failed(
                request_id,
                "Warn system is not loaded."
            )
            return

        result = await warn_cog.issue_warning(
            guild=guild,
            moderator=moderator,
            member=member,
            reason=reason
        )

        if not result["success"]:
            await self.mark_failed(
                request_id,
                result["message"]
            )
            return

        warning_number = result[
            "warning_number"
        ]

        await self.mark_completed(
            request_id,
            (
                f"Warning #{warning_number} issued "
                f"to {member}."
            )
        )

        print(
            "[Moderation Bridge] "
            f"Warning #{warning_number} issued "
            f"to {member} by {moderator}."
        )

    async def process_timeout(
        self,
        request: dict
    ):
        request_id = request["id"]

        guild_id = self.parse_id(
            request.get("guild_id")
        )

        moderator_id = self.parse_id(
            request.get("moderator_id")
        )

        target_user_id = self.parse_id(
            request.get("target_user_id")
        )

        reason = (
            request.get("reason")
            or "No reason provided"
        )

        duration = (
            request.get("duration")
            or ""
        )

        if guild_id is None:
            await self.mark_failed(
                request_id,
                "Invalid guild ID."
            )
            return

        if moderator_id is None:
            await self.mark_failed(
                request_id,
                "Invalid moderator ID."
            )
            return

        if target_user_id is None:
            await self.mark_failed(
                request_id,
                "Invalid target user ID."
            )
            return

        if not duration:
            await self.mark_failed(
                request_id,
                "Timeout duration is missing."
            )
            return

        guild = self.bot.get_guild(
            guild_id
        )

        if guild is None:
            await self.mark_failed(
                request_id,
                "Discord server could not be found."
            )
            return

        moderator = guild.get_member(
            moderator_id
        )

        if moderator is None:
            try:
                moderator = await guild.fetch_member(
                    moderator_id
                )
            except discord.NotFound:
                moderator = None
            except discord.HTTPException:
                moderator = None

        if moderator is None:
            await self.mark_failed(
                request_id,
                "Moderator could not be found in the server."
            )
            return

        member = guild.get_member(
            target_user_id
        )

        if member is None:
            try:
                member = await guild.fetch_member(
                    target_user_id
                )
            except discord.NotFound:
                member = None
            except discord.HTTPException:
                member = None

        if member is None:
            await self.mark_failed(
                request_id,
                "Target member could not be found in the server."
            )
            return

        timeout_cog = self.bot.get_cog(
            "Timeout"
        )

        if timeout_cog is None:
            await self.mark_failed(
                request_id,
                "Timeout system is not loaded."
            )
            return

        result = await timeout_cog.issue_timeout(
            guild=guild,
            moderator=moderator,
            member=member,
            duration=duration,
            reason=reason
        )

        if not result["success"]:
            await self.mark_failed(
                request_id,
                result["message"]
            )
            return

        await self.mark_completed(
            request_id,
            (
                f"{member} timed out for "
                f"{duration}."
            )
        )

        print(
            "[Moderation Bridge] "
            f"{member} timed out for "
            f"{duration} by {moderator}."
        )

    async def process_kick(
        self,
        request: dict
    ):
        request_id = request["id"]

        guild_id = self.parse_id(
            request.get("guild_id")
        )

        moderator_id = self.parse_id(
            request.get("moderator_id")
        )

        target_user_id = self.parse_id(
            request.get("target_user_id")
        )

        reason = (
            request.get("reason")
            or "No reason provided"
        )

        if guild_id is None:
            await self.mark_failed(
                request_id,
                "Invalid guild ID."
            )
            return

        if moderator_id is None:
            await self.mark_failed(
                request_id,
                "Invalid moderator ID."
            )
            return

        if target_user_id is None:
            await self.mark_failed(
                request_id,
                "Invalid target user ID."
            )
            return

        guild = self.bot.get_guild(
            guild_id
        )
        if guild is None:
            await self.mark_failed(
                request_id,
                "Discord server could not be found."
            )
            return

        moderator = guild.get_member(
            moderator_id
        )
        if moderator is None:
            try:
                moderator = await guild.fetch_member(
                    moderator_id
                )
            except discord.NotFound:
                moderator = None
            except discord.HTTPException:
                moderator = None
        if moderator is None:
            await self.mark_failed(
                request_id,
                "Moderator could not be found in the server."
            )
            return

        member = guild.get_member(
            target_user_id
        )
        if member is None:
            try:
                member = await guild.fetch_member(
                    target_user_id
                )
            except discord.NotFound:
                member = None
            except discord.HTTPException:
                member = None
        if member is None:
            await self.mark_failed(
                request_id,
                "Target member could not be found in the server."
            )
            return

        kick_cog = self.bot.get_cog(
            "Kick"
        )
        if kick_cog is None:
            await self.mark_failed(
                request_id,
                "Kick system is not loaded."
            )
            return 

        result = await kick_cog.issue_kick(
            guild=guild,
            moderator=moderator,
            member=member,
            reason=reason
        )
        if not result["success"]:
            await self.mark_failed(
                request_id,
                result["message"]
            )
            return
        await self.mark_completed(
            request_id,
            (
                f"{member} was kicked "
                f"by {moderator}."
            )
        )
        print(
            "[Moderation Bridge] "
            f"{member} was kicked "
            f"by {moderator}."
        )

    async def process_ban(
        self,
        request: dict
    ):
        request_id = request["id"]

        guild_id = self.parse_id(
            request.get("guild_id")
        )

        moderator_id = self.parse_id(
            request.get("moderator_id")
        )

        target_user_id = self.parse_id(
            request.get("target_user_id")
        )

        reason = (
            request.get("reason")
            or "No reason provided"
        )

        if guild_id is None:
            await self.mark_failed(
                request_id,
                "Invalid guild ID."
            )
            return

        if moderator_id is None:
            await self.mark_failed(
                request_id,
                "Invalid moderator ID."
            )
            return

        if target_user_id is None:
            await self.mark_failed(
                request_id,
                "Invalid target user ID."
            )
            return

        guild = self.bot.get_guild(
            guild_id
        )

        if guild is None:
            await self.mark_failed(
                request_id,
                "Discord server could not be found."
            )
            return

        moderator = guild.get_member(
            moderator_id
        )

        if moderator is None:
            try:
                moderator = await guild.fetch_member(
                    moderator_id
                )
            except discord.NotFound:
                moderator = None
            except discord.HTTPException:
                moderator = None

        if moderator is None:
            await self.mark_failed(
                request_id,
                "Moderator could not be found in the server."
            )
            return

        member = guild.get_member(
            target_user_id
        )

        if member is None:
            try:
                member = await guild.fetch_member(
                    target_user_id
                )
            except discord.NotFound:
                member = None
            except discord.HTTPException:
                member = None

        if member is None:
            await self.mark_failed(
                request_id,
                "Target member could not be found in the server."
            )
            return

        ban_cog = self.bot.get_cog(
            "Ban"
        )

        if ban_cog is None:
            await self.mark_failed(
                request_id,
                "Ban system is not loaded."
            )
            return

        result = await ban_cog.issue_ban(
            guild=guild,
            moderator=moderator,
            member=member,
            reason=reason
        )

        if not result["success"]:
            await self.mark_failed(
                request_id,
                result["message"]
            )
            return

        await self.mark_completed(
            request_id,
            (
                f"{member} was banned "
                f"by {moderator}."
            )
        )

        print(
            "[Moderation Bridge] "
            f"{member} was banned "
            f"by {moderator}."
        )

    async def process_unban(
        self,
        request: dict
    ):
        request_id = request["id"]

        guild_id = self.parse_id(
            request.get("guild_id")
        )

        moderator_id = self.parse_id(
            request.get("moderator_id")
        )

        target_user_id = self.parse_id(
            request.get("target_user_id")
        )

        reason = (
            request.get("reason")
            or "No reason provided"
        )

        if guild_id is None:
            await self.mark_failed(
                request_id,
                "Invalid guild ID."
            )
            return

        if moderator_id is None:
            await self.mark_failed(
                request_id,
                "Invalid moderator ID."
            )
            return

        if target_user_id is None:
            await self.mark_failed(
                request_id,
                "Invalid target user ID."
            )
            return

        guild = self.bot.get_guild(
            guild_id
        )

        if guild is None:
            await self.mark_failed(
                request_id,
                "Discord server could not be found."
            )
            return

        moderator = guild.get_member(
            moderator_id
        )

        if moderator is None:
            try:
                moderator = await guild.fetch_member(
                    moderator_id
                )
            except discord.NotFound:
                moderator = None
            except discord.HTTPException:
                moderator = None

        if moderator is None:
            await self.mark_failed(
                request_id,
                "Moderator could not be found in the server."
            )
            return

        try:
            user = await self.bot.fetch_user(
                target_user_id
            )

        except discord.NotFound:
            await self.mark_failed(
                request_id,
                "Discord user could not be found."
            )
            return

        except discord.HTTPException:
            await self.mark_failed(
                request_id,
                "Discord user could not be retrieved."
            )
            return

        unban_cog = self.bot.get_cog(
            "Unban"
        )

        if unban_cog is None:
            await self.mark_failed(
                request_id,
                "Unban system is not loaded."
            )
            return

        result = await unban_cog.issue_unban(
            guild=guild,
            moderator=moderator,
            user=user,
            reason=reason
        )

        if not result["success"]:
            await self.mark_failed(
                request_id,
                result["message"]
            )
            return

        await self.mark_completed(
            request_id,
            (
                f"{user} was unbanned "
                f"by {moderator}."
            )
        )

        print(
            "[Moderation Bridge] "
            f"{user} was unbanned "
            f"by {moderator}."
        )

    async def process_clear(
        self,
        request: dict
    ):
        request_id = request["id"]

        guild_id = self.parse_id(
            request.get("guild_id")
        )

        moderator_id = self.parse_id(
            request.get("moderator_id")
        )

        channel_id = self.parse_id(
            request.get("channel_id")
        )

        amount = request.get(
            "amount"
        )

        if guild_id is None:
            await self.mark_failed(
                request_id,
                "Invalid guild ID."
            )
            return

        if moderator_id is None:
            await self.mark_failed(
                request_id,
                "Invalid moderator ID."
            )
            return

        if channel_id is None:
            await self.mark_failed(
                request_id,
                "Invalid channel ID."
            )
            return

        try:
            amount = int(
                amount
            )
        except (
            TypeError,
            ValueError
        ):
            await self.mark_failed(
                request_id,
                "Invalid message amount."
            )
            return

        if amount < 1 or amount > 100:
            await self.mark_failed(
                request_id,
                "Message amount must be between 1 and 100."
            )
            return

        guild = self.bot.get_guild(
            guild_id
        )

        if guild is None:
            await self.mark_failed(
                request_id,
                "Discord server could not be found."
            )
            return

        moderator = guild.get_member(
            moderator_id
        )

        if moderator is None:
            try:
                moderator = await guild.fetch_member(
                    moderator_id
                )
            except discord.NotFound:
                moderator = None
            except discord.HTTPException:
                moderator = None

        if moderator is None:
            await self.mark_failed(
                request_id,
                "Moderator could not be found in the server."
            )
            return

        channel = guild.get_channel(
            channel_id
        )

        if channel is None:
            try:
                channel = await self.bot.fetch_channel(
                    channel_id
                )
            except (
                discord.NotFound,
                discord.Forbidden,
                discord.HTTPException
            ):
                channel = None

        if channel is None:
            await self.mark_failed(
                request_id,
                "Discord channel could not be found."
            )
            return

        if not isinstance(
            channel,
            discord.TextChannel
        ):
            await self.mark_failed(
                request_id,
                "The selected channel is not a text channel."
            )
            return

        clear_cog = self.bot.get_cog(
            "Clear"
        )

        if clear_cog is None:
            await self.mark_failed(
                request_id,
                "Clear system is not loaded."
            )
            return

        result = await clear_cog.issue_clear(
            guild=guild,
            moderator=moderator,
            channel=channel,
            amount=amount
        )

        if not result["success"]:
            await self.mark_failed(
                request_id,
                result["message"]
            )
            return

        deleted_count = result[
            "deleted_count"
        ]

        await self.mark_completed(
            request_id,
            (
                f"Deleted {deleted_count} message(s) "
                f"from #{channel.name}."
            )
        )

        print(
            "[Moderation Bridge] "
            f"{moderator} cleared "
            f"{deleted_count} message(s) "
            f"from #{channel.name}."
        )

    async def process_lock(
        self,
        request: dict
    ):
        request_id = request["id"]

        guild_id = self.parse_id(
            request.get("guild_id")
        )

        moderator_id = self.parse_id(
            request.get("moderator_id")
        )

        channel_id = self.parse_id(
            request.get("channel_id")
        )

        if guild_id is None:
            await self.mark_failed(
                request_id,
                "Invalid guild ID."
            )
            return

        if moderator_id is None:
            await self.mark_failed(
                request_id,
                "Invalid moderator ID."
            )
            return

        if channel_id is None:
            await self.mark_failed(
                request_id,
                "Invalid channel ID."
            )
            return

        guild = self.bot.get_guild(
            guild_id
        )

        if guild is None:
            await self.mark_failed(
                request_id,
                "Discord server could not be found."
            )
            return

        moderator = guild.get_member(
            moderator_id
        )

        if moderator is None:
            try:
                moderator = await guild.fetch_member(
                    moderator_id
                )
            except discord.NotFound:
                moderator = None
            except discord.HTTPException:
                moderator = None

        if moderator is None:
            await self.mark_failed(
                request_id,
                "Moderator could not be found in the server."
            )
            return

        channel = guild.get_channel(
            channel_id
        )

        if channel is None:
            try:
                channel = await self.bot.fetch_channel(
                    channel_id
                )
            except (
                discord.NotFound,
                discord.Forbidden,
                discord.HTTPException
            ):
                channel = None

        if channel is None:
            await self.mark_failed(
                request_id,
                "Discord channel could not be found."
            )
            return

        if not isinstance(
            channel,
            discord.TextChannel
        ):
            await self.mark_failed(
                request_id,
                "The selected channel is not a text channel."
            )
            return

        lock_cog = self.bot.get_cog(
            "Lock"
        )

        if lock_cog is None:
            await self.mark_failed(
                request_id,
                "Lock system is not loaded."
            )
            return

        result = await lock_cog.issue_lock(
            guild=guild,
            moderator=moderator,
            channel=channel
        )

        if not result["success"]:
            await self.mark_failed(
                request_id,
                result["message"]
            )
            return

        await self.mark_completed(
            request_id,
            (
                f"#{channel.name} was locked "
                f"by {moderator}."
            )
        )

        print(
            "[Moderation Bridge] "
            f"#{channel.name} was locked "
            f"by {moderator}."
        )

    async def process_unlock(
        self,
        request: dict
    ):
        request_id = request["id"]

        guild_id = self.parse_id(
            request.get("guild_id")
        )

        moderator_id = self.parse_id(
            request.get("moderator_id")
        )

        channel_id = self.parse_id(
            request.get("channel_id")
        )

        if guild_id is None:
            await self.mark_failed(
                request_id,
                "Invalid guild ID."
            )
            return

        if moderator_id is None:
            await self.mark_failed(
                request_id,
                "Invalid moderator ID."
            )
            return

        if channel_id is None:
            await self.mark_failed(
                request_id,
                "Invalid channel ID."
            )
            return

        guild = self.bot.get_guild(
            guild_id
        )

        if guild is None:
            await self.mark_failed(
                request_id,
                "Discord server could not be found."
            )
            return

        moderator = guild.get_member(
            moderator_id
        )

        if moderator is None:
            try:
                moderator = await guild.fetch_member(
                    moderator_id
                )
            except discord.NotFound:
                moderator = None
            except discord.HTTPException:
                moderator = None

        if moderator is None:
            await self.mark_failed(
                request_id,
                "Moderator could not be found in the server."
            )
            return

        channel = guild.get_channel(
            channel_id
        )

        if channel is None:
            try:
                channel = await self.bot.fetch_channel(
                    channel_id
                )
            except (
                discord.NotFound,
                discord.Forbidden,
                discord.HTTPException
            ):
                channel = None

        if channel is None:
            await self.mark_failed(
                request_id,
                "Discord channel could not be found."
            )
            return

        if not isinstance(
            channel,
            discord.TextChannel
        ):
            await self.mark_failed(
                request_id,
                "The selected channel is not a text channel."
            )
            return

        unlock_cog = self.bot.get_cog(
            "Unlock"
        )

        if unlock_cog is None:
            await self.mark_failed(
                request_id,
                "Unlock system is not loaded."
            )
            return

        result = await unlock_cog.issue_unlock(
            guild=guild,
            moderator=moderator,
            channel=channel
        )

        if not result["success"]:
            await self.mark_failed(
                request_id,
                result["message"]
            )
            return

        await self.mark_completed(
            request_id,
            (
                f"#{channel.name} was unlocked "
                f"by {moderator}."
            )
        )

        print(
            "[Moderation Bridge] "
            f"#{channel.name} was unlocked "
            f"by {moderator}."
        )

    async def mark_completed(
        self,
        request_id: str,
        message: str
    ):
        await asyncio.to_thread(
            lambda: (
                supabase
                .table("moderation_requests")
                .update({
                    "status": "completed",
                    "result_message": message,
                    "processed_at":
                        datetime.now(
                            timezone.utc
                        ).isoformat()
                })
                .eq("id", request_id)
                .execute()
            )
        )

    async def mark_failed(
        self,
        request_id: str,
        message: str
    ):
        await asyncio.to_thread(
            lambda: (
                supabase
                .table("moderation_requests")
                .update({
                    "status": "failed",
                    "result_message": message,
                    "processed_at":
                        datetime.now(
                            timezone.utc
                        ).isoformat()
                })
                .eq("id", request_id)
                .execute()
            )
        )

        print(
            "[Moderation Bridge] "
            f"Request {request_id} failed: {message}"
        )

    @staticmethod
    def parse_id(
        value
    ):
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

async def setup(
    bot: commands.Bot
):
    await bot.add_cog(
        ModerationBridge(bot)
    )