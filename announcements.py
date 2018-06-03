import re
import time

import discord

import client

# Constants
CHANNEL_ID = '109424003403247616'  # mod
# CHANNEL_ID = '257073315011624961'  # dev-test
ANNOUNCE_REGEX = r'^\/announce\s+<#(\d+)>\s+(.+)$'
EDIT_REGEX = r'^\/edit\s+<#(\d+)>\s+(\d+)\s+(.+)$'


async def on_ready():
    print('Accepting announcement commands in channel #{0} ({1})'.format(
        client.discordClient.get_channel(CHANNEL_ID),
        CHANNEL_ID))


async def on_message(message):
    if message.channel.id != CHANNEL_ID:
        return

    text = message.content

    match = re.search(ANNOUNCE_REGEX, text, re.DOTALL)
    if match:
        channelId = match.group(1)
        channel = client.discordClient.get_channel(channelId)
        messageStr = match.group(2)
        print('Posting a message in #{0} ({1}):\n{2}'.format(
            channel,
            CHANNEL_ID,
            messageStr))
        await client.discordClient.send_message(channel, messageStr)

    match = re.search(EDIT_REGEX, text, re.DOTALL)
    if match:
        channelId = match.group(1)
        channel = client.discordClient.get_channel(channelId)
        messageId = match.group(2)
        message = await client.discordClient.get_message(channel, messageId)
        messageStr = match.group(3)
        print('Editing message {0} in #{1} ({2}):\n{3}'.format(
            messageId,
            channel,
            CHANNEL_ID,
            messageStr))
        await client.discordClient.edit_message(message, messageStr)
