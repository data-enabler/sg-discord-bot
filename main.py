import asyncio
import logging

import discord

import client
import constants
import role_assigner
import roles
import rules


discordToken = open('token').readline().strip()
logging.basicConfig(level=logging.INFO)


@client.discordClient.event
async def on_ready():
    print('------')
    print_info()
    await role_assigner.on_ready()
    await rules.on_ready()
    await roles.on_ready()
    print('------')


def print_info():
    print('User: {0} ({1})'.format(
        client.discordClient.user.name,
        client.discordClient.user.id))
    print('Server: {0} ({1})'.format(
        client.discordClient.get_server(constants.SERVER_ID),
        constants.SERVER_ID))


@client.discordClient.event
async def on_message(message):
    await role_assigner.on_message(message)
    await rules.on_message(message)


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
