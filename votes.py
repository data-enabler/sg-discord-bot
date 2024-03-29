import re
import time

import discord

import client
import roles

# Constants
CHANNEL_IDS = [
    816863262917394463,  # 2e-beta-gameplay
    833462332553560084,  # 2e-feature-discussion
    #257073315011624961,  # dev-test
]
EXEMPT_USERS = {
    741181637244485652, # Liam
}


async def on_ready():
    print('Adding upvote emoji to messages in the following channels:')
    [
        print('{0} ({1})'.format(client.discordClient.get_channel(id), id))
        for id in CHANNEL_IDS
    ]


async def on_message(message: discord.Message):
    if message.channel.id not in CHANNEL_IDS:
        return

    if message.author.id in EXEMPT_USERS:
        return

    await message.add_reaction('👍')
