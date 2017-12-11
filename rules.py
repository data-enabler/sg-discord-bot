import re
import time

import discord

import client
import roles

# Constants
CHANNEL_ID = '388764554848632842'  # rules
# CHANNEL_ID = '257073315011624961'  # dev-test
RULE_ROLE_ID = '388565602890940416'
PHRASE_REGEX = r'^I have read and understand the rules\.?$'


async def on_ready():
    print('Listening for rule acceptance on channel #{0} ({1})'.format(
        client.discordClient.get_channel(CHANNEL_ID),
        CHANNEL_ID))


async def on_message(message):
    if message.channel.id != CHANNEL_ID:
        return

    text = message.content
    print('rules: ', text)

    foundKeyphrase = False
    if re.search(PHRASE_REGEX, text):
        foundKeyphrase = True
        await roles.reassign_roles(
            message.author,
            set([RULE_ROLE_ID]),
            set())

    reaction = '✅' if foundKeyphrase else '❌'
    await client.discordClient.add_reaction(message, reaction)

    time.sleep(1)

    await client.discordClient.delete_message(message)
