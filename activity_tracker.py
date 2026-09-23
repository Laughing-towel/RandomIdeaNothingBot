import random
from collections import deque
from datetime import datetime, timedelta, timezone

import discord


class ActivityTracker:
    def __init__(self):
        # Only lives in memory. Gone when the bot restarts.
        self.recent_messages = deque(maxlen=300)

    def record_message(self, message: discord.Message):
        # Ignore DMs
        if message.guild is None:
            return

        # Ignore bots, including ourselves
        if message.author.bot:
            return

        self.recent_messages.append(message)

    def get_recent_messages(
        self,
        guild: discord.Guild,
        minutes: int = 15,
    ):
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutes)

        return [
            message
            for message in self.recent_messages
            if (
                message.guild.id == guild.id
                and message.created_at >= cutoff
            )
        ]

    def random_recent_message(
        self,
        guild: discord.Guild,
        minutes: int = 15,
    ):
        messages = self.get_recent_messages(
            guild,
            minutes=minutes,
        )

        if not messages:
            return None

        return random.choice(messages)

    def random_active_channel(
        self,
        guild: discord.Guild,
        minutes: int = 30,
    ):
        recent = self.get_recent_messages(
            guild,
            minutes=minutes,
        )

        bot_member = guild.me

        if bot_member is None:
            return None

        usable_messages = []

        for message in recent:
            channel = message.channel

            if not isinstance(channel, discord.TextChannel):
                continue

            permissions = channel.permissions_for(bot_member)

            if (
                permissions.view_channel
                and permissions.send_messages
            ):
                usable_messages.append(message)

        # Choosing a random recent message naturally makes
        # more active channels more likely.
        if usable_messages:
            return random.choice(usable_messages).channel

        # Fall back to #general
        general = discord.utils.get(
            guild.text_channels,
            name="general",
        )

        if general is not None:
            permissions = general.permissions_for(bot_member)

            if (
                permissions.view_channel
                and permissions.send_messages
            ):
                return general

        # Absolute fallback: any channel we're allowed to speak in.
        valid_channels = []

        for channel in guild.text_channels:
            permissions = channel.permissions_for(bot_member)

            if (
                permissions.view_channel
                and permissions.send_messages
            ):
                valid_channels.append(channel)

        if not valid_channels:
            return None

        return random.choice(valid_channels)