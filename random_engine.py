import asyncio
import os
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

import discord

from activity_tracker import ActivityTracker
from fact_generator import FactGenerator


class RandomEngine:
    def __init__(
            self,
            bot: discord.Client,
            activity_tracker: ActivityTracker,
            vc_tracker,
    ):
        self.bot = bot
        self.activity = activity_tracker
        self.vc_tracker = vc_tracker

        self.facts = FactGenerator(
            self.bot,
            self.vc_tracker,
        )
        self.dev_mode = (
                os.getenv("DEV_MODE", "false").lower() == "true")

        # -----------------------------------------------------
        # Timing
        # -----------------------------------------------------

        if self.dev_mode:
            # Fast while we're testing.
            self.min_delay = 10
            self.max_delay = 30
        else:
            # Temporary production timings.
            # We'll tune these properly later.
            self.min_delay = 60 * 60
            self.max_delay = 6 * 60 * 60

        # -----------------------------------------------------
        # Random actions
        #
        # These are relative weights, not guaranteed percentages.
        # -----------------------------------------------------

        self.actions = [
            (self.do_nothing, 40),

            (self.send_random_fact, 30),
            (self.send_blank, 3),

            (self.react_to_recent_message, 8),
            (self.ask_for_idea, 6),
            (self.send_helpful_lie, 5),

            (self.join_voice, 3),

            (self.change_nickname, 2),
            (self.change_activity, 1.5),

            (self.reply_to_old_message, 2),

            (self.change_global_username, 0.5),
            (self.change_avatar, 0),
        ]
        # -----------------------------------------------------
        # Idea Bot questions
        # -----------------------------------------------------

        self.idea_questions = [
            "give me an idea for a game",
            "give me an idea for a sandwich",
            "give me an idea for a website",
            "give me an idea for a discord bot",
            "give me an idea for something to draw",
            "give me an idea for a name",
            "give me an idea for a useless invention",
            "what should I name a horse",
            "what should I do tomorrow",
            "give me an idea for a room",
            "give me an idea for a story",
            "give me an idea for dinner",
            "give me an idea for a superpower",
            "give me an idea for an app",
            "give me an idea for a pet name",
            "give me an idea for something to build",
            "give me an idea for a colour",
            "give me an idea for a username",
            "give me an idea for a movie",
            "give me an idea for something to buy",

            "what should I name my hypothetical boat",
            "give me an idea for a business",
            "what animal should be made illegal",
            "what should I put in a drawer",
            "give me an idea for a new shape",
            "what should I name a rock",
            "give me an idea for a fake country",
            "what should the national animal of my bedroom be",
            "give me an idea for a suspicious hobby",
            "what should I eat at 3am",
            "give me an idea for a weapon that would be completely useless",
            "what should I call my left shoe",
            "give me an idea for a new holiday",
            "what should I keep in my pockets at all times",
            "give me an idea for a bad superhero",
            "give me an idea for a supervillain with no useful powers",
            "what should I name a worm",
            "give me an idea for a new type of chair",
            "what should I do if I find 17 bricks",
            "give me an idea for something to scream in a cave",
            "what should I name a random pigeon",
            "give me an idea for a really bad tattoo",
            "what should I put on a flag",
            "give me an idea for a fake conspiracy theory",
            "what should I name my fridge",
            "give me an idea for a new sport",
            "what object would make the best president",
            "give me an idea for a very inconvenient superpower",
            "what should I name a sword I do not own",
            "give me an idea for a horrible restaurant",
            "what should I wear to the moon",
            "give me an idea for a new pasta shape",
            "what should I name a cloud",
            "give me an idea for a useless button",
            "what would be the worst thing to put wheels on",
            "give me an idea for a new emotion",
            "what should I do with a single grape",
            "give me an idea for a fake university degree",
            "what should I name a mosquito",
            "give me an idea for an unnecessarily complicated machine",
            "what should I put inside a very small box",
            "give me an idea for a bad alarm sound",
            "what should I call a group of accountants",
            "give me an idea for a new flavour of toothpaste",
            "what would be a terrible thing to make waterproof",
            "give me an idea for a cursed object",
            "what should I name an imaginary pub",
            "give me an idea for a new law",
            "what should I do if a goose owes me money",
            "give me an idea for a new type of door",
            "what should I name a spider",
            "give me an idea for the world's least useful robot",
            "what should I yell before entering a room",
            "give me an idea for a fake disease",
            "what should I call my future cult",
            "give me an idea for something that should have a USB port",
            "what animal would look funniest wearing jeans",
            "give me an idea for a suspicious sandwich",
            "what should I name a tiny island",
            "give me an idea for something to hide under a bed",
            "what should I put on a business card if I have no business",
            "give me an idea for a terrible password",
            "what should I name a medieval peasant",
            "give me an idea for a pointless competition",
            "what would be the worst thing to hear from your dentist",
            "give me an idea for a new type of spoon",
            "what should I name a very large fish",
            "give me an idea for a fake job",
            "what should I do if I become mayor for 8 minutes",
            "give me an idea for a new planet",
            "what should I name an evil toaster",
            "give me an idea for something to put googly eyes on",
            "what would be a good name for a haunted Tesco",
            "give me an idea for an app nobody needs",
            "what should I do with 400 rubber ducks",
            "give me an idea for a terrible theme park ride",
            "what should I name a dragon who works in accounting",
            "give me an idea for a new type of weather",
            "what should I call a secret organisation that isn't secret",
            "give me an idea for a pointless subscription service",
            "what should I name my imaginary lawyer",
            "give me an idea for something that should not be sentient",
        ]

        # -----------------------------------------------------
        # Standard reactions
        # -----------------------------------------------------

        self.reactions = [
            "👍",
            "👎",
            "😭",
            "💀",
            "🤔",
            "👀",
            "🫡",
            "❓",
            "✅",
            "🧠",
            "🥚",
            "🪑",
        ]
        self.global_usernames = [
            "RandomIdeaNothing",
            "RandomNothing",
            "IdeaNothing",
            "NothingBot",
            "SomethingBot",
            "gregbot",
            "random bot",
            "idea bot",
            "nothing bot",
        ]

        self.avatar_folder = Path("assets/avatars")

        self.last_username_change = None
        self.last_avatar_change = None

        # -----------------------------------------------------
        # Server nicknames
        #
        # None means remove the server nickname and return to
        # the bot's global username.
        # -----------------------------------------------------

        self.nicknames = [
            "RandomIdeaNothing Bot",
            "Random",
            "Idea",
            "Nothing",
            "bot",
            "greg",
            "nothing",
            "something",
            ".",
            "⠀",
            None,
        ]

        # -----------------------------------------------------
        # Presence/activity text
        #
        # These appear as "Playing ..."
        # None clears the activity.
        # -----------------------------------------------------

        self.activities = [
            None,
            "nothing",
            "thinking",
            "discord",
            "general",
            "something",
            ".",
        ]

        # -----------------------------------------------------
        # Replies to old messages
        # -----------------------------------------------------

        self.old_message_replies = [
            "ok",
            "why",
            "no",
            "yes",
            "interesting",
            "true",
            "?",
            "right",
        ]

        # -----------------------------------------------------
        # Completely truthful and reliable help messages
        # -----------------------------------------------------

        self.helpful_lies = [
            "Use `/help` to see everything I can do.",
            "Use `/ping` to check my latency.",
            "Use `/idea` whenever you need an idea.",
            "Use `/random` if you want me to do something random.",
            "Use `/stats` to view server statistics.",
            "Use `/status` to check my current status.",
            "Use `/think` if you need help thinking about something.",
            "Use `/fix` if something needs fixing.",
            "Use `/start` to start.",
            "Use `/stop` to stop.",
            "Use `/test` to make sure I'm working.",
            "Use `/hello` to say hello.",
            "Use `/work` to make me work.",
            "Use `/please` if the other commands aren't working.",
        ]

    # =========================================================
    # Main engine
    # =========================================================
    async def send_random_fact(self):
        guild = self.random_guild()

        if guild is None:
            return

        fact = await self.facts.generate(guild)

        # Some facts deliberately return None if they
        # aren't currently applicable.
        if fact is None:
            return

        channel = self.random_output_channel(guild)

        if channel is None:
            return

        await channel.send(fact)

    async def change_avatar(self):
        if self.bot.user is None:
            return

        now = datetime.now(timezone.utc)

        if self.last_avatar_change is not None:
            elapsed = (
                    now - self.last_avatar_change
            ).total_seconds()

            minimum_wait = 60 if self.dev_mode else 48 * 60 * 60

            if elapsed < minimum_wait:
                return

        if not self.avatar_folder.exists():
            return

        avatar_files = [
            path
            for path in self.avatar_folder.iterdir()
            if (
                    path.is_file()
                    and path.suffix.lower()
                    in {".png", ".jpg", ".jpeg"}
            )
        ]

        if not avatar_files:
            return

        avatar_path = random.choice(
            avatar_files
        )

        avatar_bytes = avatar_path.read_bytes()

        await self.bot.user.edit(
            avatar=avatar_bytes
        )

        self.last_avatar_change = now

    async def change_global_username(self):
        if self.bot.user is None:
            return

        now = datetime.now(timezone.utc)

        if self.last_username_change is not None:
            elapsed = (
                    now - self.last_username_change
            ).total_seconds()

            minimum_wait = 60 if self.dev_mode else 24 * 60 * 60

            if elapsed < minimum_wait:
                return

        possible_names = [
            name
            for name in self.global_usernames
            if name != self.bot.user.name
        ]

        if not possible_names:
            return

        new_name = random.choice(possible_names)

        await self.bot.user.edit(
            username=new_name
        )

        self.last_username_change = now

    async def run(self):
        await self.bot.wait_until_ready()

        print("Random engine started.")

        while not self.bot.is_closed():
            delay = random.uniform(
                self.min_delay,
                self.max_delay,
            )

            if self.dev_mode:
                print(
                    f"Next opportunity in "
                    f"{delay:.1f} seconds."
                )

            await asyncio.sleep(delay)

            actions = [
                action
                for action, weight in self.actions
            ]

            weights = [
                weight
                for action, weight in self.actions
            ]

            action = random.choices(
                actions,
                weights=weights,
                k=1,
            )[0]

            if self.dev_mode:
                print(
                    f"Random action selected: "
                    f"{action.__name__}"
                )

            try:
                await action()

            except Exception as exc:
                print(
                    f"Random action "
                    f"{action.__name__} failed: "
                    f"{type(exc).__name__}: {exc}"
                )

    # =========================================================
    # Helpers
    # =========================================================

    def random_guild(self):
        if not self.bot.guilds:
            return None

        return random.choice(self.bot.guilds)

    def random_output_channel(
            self,
            guild: discord.Guild,
    ):
        """
        Prefer recently active channels.

        The ActivityTracker handles:
        - recent activity
        - #general fallback
        - any other usable text channel as last resort
        """

        return self.activity.random_active_channel(
            guild,
            minutes=30,
        )

    # =========================================================
    # Nothing Bot
    # =========================================================

    async def do_nothing(self):
        return

    # =========================================================
    # Blank message
    # =========================================================

    async def send_blank(self):
        guild = self.random_guild()

        if guild is None:
            return

        channel = self.random_output_channel(guild)

        if channel is None:
            return

        # U+2800 BRAILLE PATTERN BLANK
        await channel.send("\u2800")

    # =========================================================
    # Server observations
    # =========================================================

    # =========================================================
    # Helpful lies
    # =========================================================

    async def send_helpful_lie(self):
        guild = self.random_guild()

        if guild is None:
            return

        channel = self.random_output_channel(guild)

        if channel is None:
            return

        message = random.choice(
            self.helpful_lies
        )

        await channel.send(message)

    # =========================================================
    # Reactions
    # =========================================================

    async def react_to_recent_message(self):
        guild = self.random_guild()

        if guild is None:
            return

        message = self.activity.random_recent_message(
            guild,
            minutes=15,
        )

        if message is None:
            return

        # Sometimes use a custom emoji from the server.
        usable_custom_emojis = [
            emoji
            for emoji in guild.emojis
            if emoji.available
        ]

        if (
                usable_custom_emojis
                and random.random() < 0.35
        ):
            emoji = random.choice(
                usable_custom_emojis
            )
        else:
            emoji = random.choice(
                self.reactions
            )

        await message.add_reaction(emoji)

    # =========================================================
    # Idea Bot
    # =========================================================

    async def ask_for_idea(self):
        guild = self.random_guild()

        if guild is None:
            return

        # Only reply to someone who's been talking recently.
        message = self.activity.random_recent_message(
            guild,
            minutes=10,
        )

        if message is None:
            return

        question = random.choice(
            self.idea_questions
        )

        await message.reply(
            question,
            mention_author=False,
        )

    # =========================================================
    # Voice chat
    # =========================================================

    async def join_voice(self):
        guild = self.random_guild()

        if guild is None:
            return

        # Already connected somewhere in this server.
        if guild.voice_client is not None:
            return

        bot_member = guild.me

        if bot_member is None:
            return

        possible_channels = []

        for channel in guild.voice_channels:
            human_members = [
                member
                for member in channel.members
                if not member.bot
            ]

            permissions = channel.permissions_for(
                bot_member
            )

            if (
                    human_members
                    and permissions.connect
            ):
                possible_channels.append(
                    channel
                )

        # Nobody is in VC / no usable VC.
        if not possible_channels:
            return

        channel = random.choice(
            possible_channels
        )

        voice_client = await channel.connect()

        if self.dev_mode:
            stay_time = random.uniform(
                5,
                20,
            )
        else:
            stay_time = random.uniform(
                5,
                90,
            )

        if self.dev_mode:
            print(
                f"Joined voice channel "
                f"{channel.name} for "
                f"{stay_time:.1f} seconds."
            )

        try:
            await asyncio.sleep(
                stay_time
            )

        finally:
            if voice_client.is_connected():
                await voice_client.disconnect()

    # =========================================================
    # Server nickname
    # =========================================================

    async def change_nickname(self):
        guild = self.random_guild()

        if guild is None:
            return

        member = guild.me

        if member is None:
            return

        nickname = random.choice(
            self.nicknames
        )

        await member.edit(
            nick=nickname,
            reason="RandomIdeaNothing Bot",
        )

    # =========================================================
    # Presence / activity
    # =========================================================

    async def change_activity(self):
        activity_name = random.choice(
            self.activities
        )

        if activity_name is None:
            activity = None
        else:
            activity = discord.Game(
                name=activity_name
            )

        await self.bot.change_presence(
            activity=activity
        )

    # =========================================================
    # Old-message archaeology
    # =========================================================

    async def reply_to_old_message(self):
        guild = self.random_guild()

        if guild is None:
            return

        channel = self.random_output_channel(
            guild
        )

        if channel is None:
            return

        now = datetime.now(
            timezone.utc
        )

        # Nothing newer than one week counts as old.
        newest_allowed = (
                now - timedelta(days=7)
        )

        # Don't search beyond two years or before the
        # server itself existed.
        oldest_allowed = max(
            guild.created_at,
            now - timedelta(days=730),
        )

        if (
                oldest_allowed
                >= newest_allowed
        ):
            return

        total_seconds = (
                newest_allowed
                - oldest_allowed
        ).total_seconds()

        random_offset = random.uniform(
            0,
            total_seconds,
        )

        random_date = (
                oldest_allowed
                + timedelta(
            seconds=random_offset
        )
        )

        messages = [
            message
            async for message in channel.history(
                limit=50,
                before=random_date,
            )
            if (
                    not message.author.bot
                    and message.content.strip()
            )
        ]

        if not messages:
            return

        message = random.choice(
            messages
        )

        reply = random.choice(
            self.old_message_replies
        )

        await message.reply(
            reply,
            mention_author=False,
        )
