import os
import asyncio

import discord
from discord import app_commands
from dotenv import load_dotenv

from nothing_commands import register_nothing_commands
from random_engine import RandomEngine
from activity_tracker import ActivityTracker
from vc_tracker import VCTracker

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
TEST_GUILD_ID = os.getenv("TEST_GUILD_ID")


if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN is missing from .env")

if TEST_GUILD_ID:
    TEST_GUILD_ID = int(TEST_GUILD_ID)


intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True


class RandomIdeaNothingBot(discord.Client):

    def __init__(self):
        super().__init__(
            intents=intents,
             allowed_mentions=discord.AllowedMentions.none(),
        )
        self.activity_tracker = ActivityTracker()
        self.vc_tracker = VCTracker()

        self.random_engine = RandomEngine(
            self,
            self.activity_tracker,
            self.vc_tracker,
        )

        self.tree = app_commands.CommandTree(self)

        self.activity_tracker = ActivityTracker()

        self.random_engine = RandomEngine(
            self,
            self.activity_tracker,
            self.vc_tracker,
        )

    async def on_voice_state_update(
            self,
            member: discord.Member,
            before: discord.VoiceState,
            after: discord.VoiceState,
    ):
        # Joined voice from nowhere
        if before.channel is None and after.channel is not None:
            self.vc_tracker.member_joined_vc(member)

        # Completely left voice
        elif before.channel is not None and after.channel is None:
            self.vc_tracker.member_left_vc(member)

        # Moving VC -> VC doesn't reset the timer.

    async def on_message(self, message: discord.Message):
        self.activity_tracker.record_message(message)

    async def setup_hook(self):
        register_nothing_commands(self.tree)

        if TEST_GUILD_ID:
            guild = discord.Object(id=TEST_GUILD_ID)

            self.tree.copy_global_to(guild=guild)

            synced = await self.tree.sync(guild=guild)

            print(
                f"Synced {len(synced)} commands "
                f"to test server {TEST_GUILD_ID}"
            )

        else:
            synced = await self.tree.sync()

            print(f"Synced {len(synced)} global commands")

        asyncio.create_task(self.random_engine.run())

    async def on_ready(self):
        self.vc_tracker.seed_existing_members(
            self.guilds
        )

        print(f"Logged in as {self.user}")
        print(f"Bot ID: {self.user.id}")
        print(
            f"Connected to "
            f"{len(self.guilds)} server(s)"
        )

bot = RandomIdeaNothingBot()

bot.run(TOKEN)