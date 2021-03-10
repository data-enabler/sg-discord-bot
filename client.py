import discord

intents = discord.Intents.default()
intents.typing = False

discordClient: discord.Client = discord.Client(intents=intents)
