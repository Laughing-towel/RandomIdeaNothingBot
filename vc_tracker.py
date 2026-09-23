from collections import defaultdict
from datetime import datetime, timezone, timedelta

import discord


class VCTracker:
    def __init__(self):
        # (guild_id, user_id) -> datetime they entered VC
        self.active_sessions = {}

        # (guild_id, user_id, YYYY-MM-DD) -> seconds
        self.daily_totals = defaultdict(float)

        self.seeded = False

    def _key(self, guild_id: int, user_id: int):
        return guild_id, user_id

    def member_joined_vc(self, member: discord.Member):
        if member.bot:
            return

        key = self._key(
            member.guild.id,
            member.id,
        )

        # Don't overwrite an existing session.
        if key in self.active_sessions:
            return

        self.active_sessions[key] = datetime.now(timezone.utc)

    def member_left_vc(self, member: discord.Member):
        if member.bot:
            return

        key = self._key(
            member.guild.id,
            member.id,
        )

        joined_at = self.active_sessions.pop(
            key,
            None,
        )

        if joined_at is None:
            return

        now = datetime.now(timezone.utc)

        self._store_session(
            member.guild.id,
            member.id,
            joined_at,
            now,
        )

    def _store_session(
        self,
        guild_id: int,
        user_id: int,
        start: datetime,
        end: datetime,
    ):
        """
        Split a session across UTC dates if it crosses midnight.
        """

        current = start

        while current.date() < end.date():
            next_midnight = (
                current.replace(
                    hour=0,
                    minute=0,
                    second=0,
                    microsecond=0,
                )
                + timedelta(days=1)
            )

            seconds = (
                next_midnight - current
            ).total_seconds()

            self.daily_totals[
                guild_id,
                user_id,
                current.date(),
            ] += seconds

            current = next_midnight

        seconds = (
            end - current
        ).total_seconds()

        self.daily_totals[
            guild_id,
            user_id,
            current.date(),
        ] += seconds

    def get_today_seconds(
        self,
        guild_id: int,
        user_id: int,
    ) -> float:
        now = datetime.now(timezone.utc)
        today = now.date()

        total = self.daily_totals[
            guild_id,
            user_id,
            today,
        ]

        key = self._key(
            guild_id,
            user_id,
        )

        joined_at = self.active_sessions.get(key)

        if joined_at is not None:
            midnight = now.replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
            )

            effective_start = max(
                joined_at,
                midnight,
            )

            total += (
                now - effective_start
            ).total_seconds()

        return total

    def seed_existing_members(
        self,
        guilds: list[discord.Guild],
    ):
        """
        When the bot starts, begin timing people already in VC.

        We don't know when they actually joined before the bot came
        online, so their session begins from the bot's startup time.
        """

        if self.seeded:
            return

        now = datetime.now(timezone.utc)

        for guild in guilds:
            for channel in guild.voice_channels:
                for member in channel.members:
                    if member.bot:
                        continue

                    key = self._key(
                        guild.id,
                        member.id,
                    )

                    self.active_sessions[key] = now

        self.seeded = True