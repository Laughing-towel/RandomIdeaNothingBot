import discord
from discord import app_commands


NOTHING_COMMANDS = [
    ("help", "Show available commands."),
    ("ping", "Check the bot's latency."),
    ("nothing", "Do nothing."),
    ("idea", "Get an idea."),
    ("random", "Do something random."),
    ("think", "Think about something."),
    ("fix", "Fix something."),
    ("start", "Start."),
    ("stop", "Stop."),
    ("status", "Check the bot's current status."),
    ("stats", "View server statistics."),
    ("hello", "Hi!"),
    ("test", "Test the bot."),
    ("work", "Make the bot work."),
    ("please", "Ask nicely."),
    ("why", "Find out why."),
    ("do", "Do something."),
]


def register_nothing_commands(tree: app_commands.CommandTree) -> None:
    for name, description in NOTHING_COMMANDS:

        async def do_nothing(interaction: discord.Interaction) -> None:
            return

        command = app_commands.Command(
            name=name,
            description=description,
            callback=do_nothing,
        )

        tree.add_command(command)