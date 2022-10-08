import re
import time
from typing import Optional, Union, cast

import discord

import client

# Constants
CHANNEL_ID = 664753886631952385  # molly
# CHANNEL_ID = 387621111812063232  # admin
# CHANNEL_ID = 109424003403247616  # mod
# CHANNEL_ID = 257073315011624961  # dev-test
ANNOUNCE_REGEX = r'^\/announce\s+<#(\d+)>\s+(.+)$'
EDIT_REGEX = r'^\/edit\s+<#(\d+)>\s+(\d+)\s+(.+)$'

intents = {
    "guilds",  # discord.Intents.guilds
    "members",  # discord.Intents.members
    "guild_messages",  # discord.Intents.guild_messages
    "message_content",  # discord.Intents.message_content
}


def init(discord_client: discord.Client):
    async def on_ready():
        print('Accepting announcement commands in channel #{0} ({1})'.format(
            discord_client.get_channel(CHANNEL_ID),
            CHANNEL_ID))

    async def on_message(message: discord.Message):
        if message.channel.id != CHANNEL_ID:
            return

        text = message.content

        match = re.search(ANNOUNCE_REGEX, text, re.DOTALL)
        if match:
            channel_id = int(match.group(1))
            channel = get_destination_channel(discord_client, channel_id)
            if not channel:
                await message.channel.send(
                    content='Channel not found: {0}'.format(channel_id),
                )
                return
            message_str = match.group(2)
            print('Posting a message in #{0} ({1}):\n{2}'.format(
                channel,
                CHANNEL_ID,
                message_str))
            await channel.send(content=message_str)

        match = re.search(EDIT_REGEX, text, re.DOTALL)
        if match:
            channel_id = int(match.group(1))
            channel = get_destination_channel(discord_client, channel_id)
            if not channel:
                await message.channel.send(
                    content='Channel not found: {0}'.format(channel_id),
                )
                return
            message_id = int(match.group(2))
            message_str = match.group(3)
            try:
                messageToEdit = await channel.fetch_message(message_id)
                print('Editing message {0} in #{1} ({2}):\n{3}'.format(
                    message_id,
                    channel,
                    CHANNEL_ID,
                    message_str))
                await messageToEdit.edit(content=message_str)
            except discord.NotFound:
                await message.channel.send(
                    content='Message not found: {0}'.format(message_id),
                )

    return {
        on_ready,
        on_message,
    }


def get_destination_channel(
    client: discord.Client,
    channel_id: int,
) -> Optional[discord.TextChannel]:
    channel = cast(
        Optional[Union[
            discord.abc.GuildChannel,
            discord.Thread,
            discord.DMChannel,
            discord.GroupChannel,
        ]],
        client.get_channel(channel_id),
    )
    if channel is None or channel.type is not discord.ChannelType.text:
        return None
    return cast(discord.TextChannel, channel)
