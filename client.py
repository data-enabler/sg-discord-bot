from typing import Iterable
import discord
from discord.ext import commands


def init_client(intents: Iterable[str]) -> commands.Bot:
    intents_obj = discord.Intents(**{key: True for key in intents})
    return commands.Bot(
        intents=intents_obj,
        command_prefix='/',
        description='Your friendly neighborhood Skullgirls Discord bot',
    )
