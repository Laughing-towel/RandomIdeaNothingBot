import random
from datetime import datetime, timezone
from message_search import MessageSearch
import discord


class FactGenerator:
    def __init__(
            self,
            bot: discord.Client,
            vc_tracker,
    ):
        self.search = MessageSearch(bot)
        self.vc_tracker = vc_tracker

        self.fact_generators = [
            self.messages_today,
            self.random_member_messages_today,
            self.random_member_total_messages,
            self.random_member_vc_time_today,
        ]

    async def random_member_vc_time_today(
            self,
            guild: discord.Guild,
    ):
        members = [
            member
            for member in guild.members
            if not member.bot
        ]

        if not members:
            return None

        member = random.choice(members)

        seconds = self.vc_tracker.get_today_seconds(
            guild.id,
            member.id,
        )

        # If they've spent no tracked time in VC today,
        # just abandon this fact.
        if seconds < 60:
            return None

        total_minutes = int(seconds // 60)

        hours = total_minutes // 60
        minutes = total_minutes % 60

        if hours == 0:
            return (
                f"{member.display_name} has spent "
                f"{minutes} minutes in voice chat today."
            )

        if minutes == 0:
            if hours == 1:
                return (
                    f"{member.display_name} has spent "
                    f"1 hour in voice chat today."
                )

            return (
                f"{member.display_name} has spent "
                f"{hours} hours in voice chat today."
            )

        if hours == 1:
            return (
                f"{member.display_name} has spent "
                f"1 hour and {minutes} minutes "
                f"in voice chat today."
            )

        return (
            f"{member.display_name} has spent "
            f"{hours} hours and {minutes} minutes "
            f"in voice chat today."
        )

    async def generate(
        self,
        guild: discord.Guild,
    ) -> str | None:

        generator = random.choice(
            self.fact_generators
        )

        return await generator(guild)

    # =========================================================
    # Message-search facts
    # =========================================================

    async def messages_today(
        self,
        guild: discord.Guild,
    ):
        now = datetime.now(timezone.utc)

        midnight = now.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

        count = await self.search.count_messages(
            guild,
            after=midnight,
            humans_only=True,
        )

        if count is None:
            return None

        if count == 1:
            return "1 message has been sent today."

        return f"{count} messages have been sent today."

    async def random_member_messages_today(
        self,
        guild: discord.Guild,
    ):
        member = self.random_human_member(guild)

        if member is None:
            return None

        now = datetime.now(timezone.utc)

        midnight = now.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

        count = await self.search.count_messages(
            guild,
            author_id=member.id,
            after=midnight,
        )

        if count is None:
            return None

        if count == 1:
            return (
                f"{member.display_name} has sent "
                f"1 message today."
            )

        return (
            f"{member.display_name} has sent "
            f"{count} messages today."
        )

    async def random_member_total_messages(
        self,
        guild: discord.Guild,
    ):
        member = self.random_human_member(guild)

        if member is None:
            return None

        count = await self.search.count_messages(
            guild,
            author_id=member.id,
        )

        if count is None:
            return None

        if count == 1:
            return (
                f"{member.display_name} has sent "
                f"1 message in this server."
            )

        return (
            f"{member.display_name} has sent "
            f"{count} messages in this server."
        )

    # =========================================================
    # Basic server facts
    # =========================================================

    async def server_age(
        self,
        guild: discord.Guild,
    ):
        now = datetime.now(timezone.utc)

        days = (
            now - guild.created_at
        ).days

        return (
            f"This server was created "
            f"{days} days ago."
        )

    async def member_count(
        self,
        guild: discord.Guild,
    ):
        count = guild.member_count

        if count is None:
            count = len(guild.members)

        if count == 1:
            return "There is 1 member in this server."

        return (
            f"There are {count} members "
            f"in this server."
        )

    async def bot_count(
        self,
        guild: discord.Guild,
    ):
        count = len([
            member
            for member in guild.members
            if member.bot
        ])

        if count == 1:
            return "There is 1 bot in this server."

        return (
            f"There are {count} bots "
            f"in this server."
        )

    async def text_channel_count(
        self,
        guild: discord.Guild,
    ):
        count = len(guild.text_channels)

        if count == 1:
            return "There is 1 text channel."

        return f"There are {count} text channels."

    async def voice_channel_count(
        self,
        guild: discord.Guild,
    ):
        count = len(guild.voice_channels)

        if count == 1:
            return "There is 1 voice channel."

        return f"There are {count} voice channels."

    async def role_count(
        self,
        guild: discord.Guild,
    ):
        # Don't count @everyone.
        count = len([
            role
            for role in guild.roles
            if not role.is_default()
        ])

        if count == 1:
            return "There is 1 role."

        return f"There are {count} roles."

    async def emoji_count(
        self,
        guild: discord.Guild,
    ):
        count = len(guild.emojis)

        if count == 1:
            return "This server has 1 custom emoji."

        return (
            f"This server has "
            f"{count} custom emojis."
        )

    # =========================================================
    # Presence facts
    # =========================================================

    async def online_count(
        self,
        guild: discord.Guild,
    ):
        count = len([
            member
            for member in guild.members
            if (
                not member.bot
                and member.status
                != discord.Status.offline
            )
        ])

        if count == 1:
            return "1 person is online."

        return f"{count} people are online."

    async def idle_count(
        self,
        guild: discord.Guild,
    ):
        count = len([
            member
            for member in guild.members
            if (
                not member.bot
                and member.status
                == discord.Status.idle
            )
        ])

        if count == 0:
            return None

        if count == 1:
            return "1 person is idle."

        return f"{count} people are idle."

    async def dnd_count(
        self,
        guild: discord.Guild,
    ):
        count = len([
            member
            for member in guild.members
            if (
                not member.bot
                and member.status
                == discord.Status.dnd
            )
        ])

        if count == 0:
            return None

        if count == 1:
            return (
                "1 person has do not disturb on."
            )

        return (
            f"{count} people have "
            f"do not disturb on."
        )

    # =========================================================
    # Voice facts
    # =========================================================

    async def voice_member_count(
        self,
        guild: discord.Guild,
    ):
        members = []

        for channel in guild.voice_channels:
            members.extend([
                member
                for member in channel.members
                if not member.bot
            ])

        count = len(members)

        if count == 0:
            return None

        if count == 1:
            return "1 person is in voice chat."

        return (
            f"{count} people are in voice chat."
        )

    async def active_voice_channel_count(
        self,
        guild: discord.Guild,
    ):
        active_channels = [
            channel
            for channel in guild.voice_channels
            if any(
                not member.bot
                for member in channel.members
            )
        ]

        count = len(active_channels)

        if count == 0:
            return None

        if count == 1:
            return (
                "1 voice channel is currently active."
            )

        return (
            f"{count} voice channels are "
            f"currently active."
        )

    # =========================================================
    # Member facts
    # =========================================================

    def random_human_member(
        self,
        guild: discord.Guild,
    ):
        members = [
            member
            for member in guild.members
            if not member.bot
        ]

        if not members:
            return None

        return random.choice(members)

    async def random_member_join_age(
        self,
        guild: discord.Guild,
    ):
        possible = [
            member
            for member in guild.members
            if (
                not member.bot
                and member.joined_at is not None
            )
        ]

        if not possible:
            return None

        member = random.choice(possible)

        now = datetime.now(timezone.utc)

        days = (
            now - member.joined_at
        ).days

        if days == 1:
            return (
                f"{member.display_name} joined "
                f"the server 1 day ago."
            )

        return (
            f"{member.display_name} joined "
            f"the server {days} days ago."
        )

    async def random_member_account_age(
        self,
        guild: discord.Guild,
    ):
        member = self.random_human_member(guild)

        if member is None:
            return None

        now = datetime.now(timezone.utc)

        days = (
            now - member.created_at
        ).days

        if days == 1:
            return (
                f"{member.display_name}'s account "
                f"was created 1 day ago."
            )

        return (
            f"{member.display_name}'s account "
            f"was created {days} days ago."
        )

    async def random_member_role_count(
        self,
        guild: discord.Guild,
    ):
        member = self.random_human_member(guild)

        if member is None:
            return None

        roles = [
            role
            for role in member.roles
            if not role.is_default()
        ]

        count = len(roles)

        if count == 1:
            return (
                f"{member.display_name} has 1 role."
            )

        return (
            f"{member.display_name} has "
            f"{count} roles."
        )

    # =========================================================
    # Oldest / newest members
    # =========================================================

    async def oldest_member(
        self,
        guild: discord.Guild,
    ):
        members = [
            member
            for member in guild.members
            if (
                not member.bot
                and member.joined_at is not None
            )
        ]

        if not members:
            return None

        member = min(
            members,
            key=lambda m: m.joined_at,
        )

        return (
            f"{member.display_name} has been "
            f"in this server the longest."
        )

    async def newest_member(
        self,
        guild: discord.Guild,
    ):
        members = [
            member
            for member in guild.members
            if (
                not member.bot
                and member.joined_at is not None
            )
        ]

        if not members:
            return None

        member = max(
            members,
            key=lambda m: m.joined_at,
        )

        return (
            f"{member.display_name} is the "
            f"newest member of this server."
        )

    # =========================================================
    # Role facts
    # =========================================================

    async def random_role_member_count(
        self,
        guild: discord.Guild,
    ):
        roles = [
            role
            for role in guild.roles
            if (
                not role.is_default()
                and not role.managed
            )
        ]

        if not roles:
            return None

        role = random.choice(roles)

        count = len(role.members)

        if count == 1:
            return (
                f"{role.name} has 1 member."
            )

        return (
            f"{role.name} has {count} members."
        )

    # =========================================================
    # Channel facts
    # =========================================================

    async def random_channel_age(
        self,
        guild: discord.Guild,
    ):
        channels = [
            *guild.text_channels,
            *guild.voice_channels,
        ]

        if not channels:
            return None

        channel = random.choice(channels)

        now = datetime.now(timezone.utc)

        days = (
            now - channel.created_at
        ).days

        if days == 1:
            return (
                f"{channel.name} was created "
                f"1 day ago."
            )

        return (
            f"{channel.name} was created "
            f"{days} days ago."
        )