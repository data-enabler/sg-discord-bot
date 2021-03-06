import asyncio
import logging
import sys

import discord

import announcements
import client
import constants
import role_assigner
import roles
import rules


discordToken = open('token').readline().strip()
logging.basicConfig(level=logging.INFO)


@client.discordClient.event
async def on_ready():
    try:
        print('------')
        print_info()
        await roles.on_ready()
        await role_assigner.on_ready()
        await rules.on_ready()
        await announcements.on_ready()
        print('------')
    except:
        print("Unexpected error:", sys.exc_info()[0])
        sys.exit('Exiting')

def print_info():
    print('User: {0} ({1})'.format(
        client.discordClient.user.name,
        client.discordClient.user.id))
    print('Server: {0} ({1})'.format(
        client.discordClient.get_guild(constants.SERVER_ID),
        constants.SERVER_ID))


@client.discordClient.event
async def on_message(message: discord.Message):
    await role_assigner.on_message(message)
    await rules.on_message(message)
    await announcements.on_message(message)


async def discord_task():
    await client.discordClient.login(discordToken, bot=True)
    await client.discordClient.connect()


def main():
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(discord_task())
    except:
        print('Shutting down...')
        loop.run_until_complete(client.discordClient.logout())
    finally:
        loop.close()


if __name__ == '__main__':
    main()
