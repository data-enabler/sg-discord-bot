import asyncio
from itertools import chain, groupby
import logging
from typing import Callable, Coroutine, Optional

import discord
import discord.ext

import announcements
import action_log
import client
import commands
import constants
import nuclino_api
# import role_assigner
# import roles
# import rules
# import votes

logging.basicConfig(level=logging.INFO)

discord_token = open('token').readline().strip()
nuclino_key = open('nuclino_api_key').readline().strip()
discord_client = client.init_client(set.union(
    action_log.intents,
    announcements.intents,
    commands.intents,
))
nuclino_client = nuclino_api.init_client(nuclino_key)


async def on_ready():
    assert discord_client.user is not None
    print('User: {0} ({1})'.format(
        discord_client.user.name,
        discord_client.user.id))
    guild: Optional[discord.Guild] = discord_client.get_guild(
        constants.SERVER_ID,
    )
    assert guild is not None
    print('Server: {0} ({1})'.format(
        guild.name,
        guild.id))


async def on_message(message: discord.Message):
    await discord_client.process_commands(message)


def register_events(handlers: list[set[Callable[..., Coroutine]]]):
    key_func: Callable[[Callable], str] = lambda f: f.__name__
    grouped_handlers = groupby(
        sorted(chain.from_iterable(handlers), key=key_func),
        key_func,
    )
    for event_name, event_handlers in grouped_handlers:
        discord_client.event(create_handler(event_name, list(event_handlers)))


def create_handler(name: str, handlers: list[Callable[..., Coroutine]]):
    print(name, [h.__qualname__ for h in handlers])

    async def handler_func(*args):
        await asyncio.gather(
            *[e(*args) for e in handlers]
        )
    handler_func.__name__ = name
    return handler_func


register_events([
    {on_ready, on_message},
    action_log.init(discord_client, nuclino_client),
    announcements.init(discord_client),
    commands.init(discord_client),
])


async def main():
    async with discord_client:
        await discord_client.start(discord_token)


if __name__ == '__main__':
    asyncio.run(main())
