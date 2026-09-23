from datetime import datetime

import discord
from discord.http import Route


class MessageSearch:
    def __init__(self, bot: discord.Client):
        self.bot = bot

    async def count_messages(
        self,
        guild: discord.Guild,
        *,
        author_id: int | None = None,
        after: datetime | None = None,
        humans_only: bool = False,
    ) -> int | None:
        """
        Count guild messages matching the supplied filters.

        Returns None if Discord's search index isn't currently ready
        or the response doesn't contain a count.
        """

        params = {
            # We don't actually care about receiving messages.
            # We only want total_results.
            "limit": 1,
        }

        if author_id is not None:
            params["author_id"] = str(author_id)

        if after is not None:
            # Discord snowflakes contain timestamps.
            # min_id means messages after this point.
            params["min_id"] = str(
                discord.utils.time_snowflake(
                    after,
                    high=False,
                )
            )

        if humans_only:
            params["author_type"] = "user"

        route = Route(
            "GET",
            "/guilds/{guild_id}/messages/search",
            guild_id=guild.id,
        )

        data = await self.bot.http.request(
            route,
            params=params,
        )

        # Discord can return an indexing response instead of
        # search results. In that case, just let this random
        # opportunity quietly produce nothing.
        if "total_results" not in data:
            return None

        return int(data["total_results"])