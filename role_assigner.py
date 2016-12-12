import discord
import getpass
import asyncio
import logging

logging.basicConfig(level=logging.INFO)


# Credentials
discordEmail = input('Discord Email: ')
discordPassword = getpass.getpass('Password: ')


# Constants
SG_SERVER_ID = '93912070059196416'
ASSIGNMENT_CHANNEL_ID = '233106056086159363'  # region-assignment
# ASSIGNMENT_CHANNEL_ID = '257073315011624961'  # dev-test


# Roles
# Each role group contains roles which are mutually excusive, and contains a
# mapping from case-insensitive trigger keyword to role id
regions = {
    "na east": "233093800506032128",
    "na central": "233093905141202946",
    "na west": "233093715231506432",
    "south america": "233095632297000960",
    "europe east": "233095260471820288",
    "europe west": "233095347197444106",
    "asia east": "233095545852395522",
    "asia southeast": "233095608179621892",
    "oceania": "233621433702416385",
}
roleGroups = [regions]
rolesById = {}


# Discord #
discordClient = discord.Client()


async def discord_task():
    await discordClient.login(discordEmail, discordPassword)
    await discordClient.connect()


@discordClient.event
async def on_message(message):
    if message.channel.id != ASSIGNMENT_CHANNEL_ID:
        return
    print('on_message:')

    text = message.content.lower()
    print(text)
    for roleGroup in roleGroups:
        for keyphrase in roleGroup.keys():
            if text.find(keyphrase) > -1:
                print('found:', keyphrase)
                await reassignRole(
                    message.author,
                    roleGroup[keyphrase],
                    roleGroup.values())
                break


async def reassignRole(member, roleId, roleGroupIds):
    roleToAdd = rolesById[roleId]
    rolesToRemove = [rolesById[r] for r in roleGroupIds if r != roleId]
    print('member:', member)
    print('adding:', roleToAdd)
    print('removing:', [r.name for r in rolesToRemove])
    newRoles = [r for r in member.roles if r not in rolesToRemove]
    newRoles.append(roleToAdd)
    print('new roles:', [r.name for r in newRoles])

    await discordClient.replace_roles(member, *newRoles)


@discordClient.event
async def on_ready():
    global rolesById
    print('Discord: logged in as {0} ({1})'.format(
        discordClient.user.name,
        discordClient.user.id))
    print('------')

    rolesById = parseRoles(discordClient.get_server(SG_SERVER_ID))


def parseRoles(server):
    return {role.id: role for role in server.roles}


def main():
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(discord_task())
    except:
        print('Shutting down...')
        loop.run_until_complete(discordClient.logout())
    finally:
        loop.close()


if __name__ == '__main__':
    main()
