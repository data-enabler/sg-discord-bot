import discord
from discord.ext import commands

intents = discord.Intents.none()
intents.emojis = True
intents.guild_messages = True
intents.guild_reactions = True
intents.guilds = True
intents.members = True

discordClient: discord.Client = commands.Bot(
	intents=intents,
	command_prefix='/',
	description='Your friendly neighborhood Skullgirls Discord bot',
)
