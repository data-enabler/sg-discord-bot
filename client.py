import discord

intents = discord.Intents.none()
intents.emojis = True
intents.guild_messages = True
intents.guild_reactions = True
intents.guilds = True
intents.members = True

discordClient: discord.Client = discord.Client(intents=intents)
