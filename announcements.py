import re
import time
from typing import Optional

import discord

import client

# Constants
CHANNEL_ID = 664753886631952385  # molly
# CHANNEL_ID = 387621111812063232  # admin
# CHANNEL_ID = 109424003403247616  # mod
# CHANNEL_ID = 257073315011624961  # dev-test
ANNOUNCE_REGEX = r'^\/announce\s+<#(\d+)>\s+(.+)$'
EDIT_REGEX = r'^\/edit\s+<#(\d+)>\s+(\d+)\s+(.+)$'


async def on_ready():
    print('Accepting announcement commands in channel #{0} ({1})'.format(
        client.discordClient.get_channel(CHANNEL_ID),
        CHANNEL_ID))


async def on_message(message: discord.Message):
    if message.channel.id != CHANNEL_ID:
        return

    text = message.content

    match = re.search(ANNOUNCE_REGEX, text, re.DOTALL)
    if match:
        channelId = int(match.group(1))
        channel: Optional[discord.TextChannel] = client.discordClient.get_channel(channelId)
        if not channel:
            await message.channel.send(content='Channel not found: {0}'.format(channelId))
            return
        messageStr = match.group(2)
        print('Posting a message in #{0} ({1}):\n{2}'.format(
            channel,
            CHANNEL_ID,
            messageStr))
        await channel.send(content=messageStr)

    match = re.search(EDIT_REGEX, text, re.DOTALL)
    if match:
        channelId = int(match.group(1))
        channel: Optional[discord.TextChannel] = client.discordClient.get_channel(channelId)
        if not channel:
            await message.channel.send(content='Channel not found: {0}'.format(channelId))
            return
        messageId = int(match.group(2))
        messageStr = match.group(3)
        try:
            messageToEdit: discord.Message = await channel.fetch_message(messageId)
            print('Editing message {0} in #{1} ({2}):\n{3}'.format(
                messageId,
                channel,
                CHANNEL_ID,
                messageStr))
            await messageToEdit.edit(content=messageStr)
        except discord.NotFound:
            await message.channel.send(content='Message not found: {0}'.format(messageId))
