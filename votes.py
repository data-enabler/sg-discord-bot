import re
import time

import discord

import client
import roles

# Constants
CHANNEL_ID = 816863262917394463  # 2e-beta-discussion
# CHANNEL_ID = 257073315011624961  # dev-test
EXEMPT_USERS = {
    741181637244485652, # Liam
}


async def on_ready():
    print('Adding up/downvote emoji to messages in channel #{0} ({1})'.format(
        client.discordClient.get_channel(CHANNEL_ID),
        CHANNEL_ID))


async def on_message(message: discord.Message):
    if message.channel.id != CHANNEL_ID:
        return

    if message.author.id in EXEMPT_USERS:
        return

    await message.add_reaction('👍')
    await message.add_reaction('👎')
