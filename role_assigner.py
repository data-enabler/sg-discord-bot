import discord
import asyncio
import logging

logging.basicConfig(level=logging.INFO)


# Credentials
discordToken = open('token').readline().strip()


# Constants
SERVER_ID = '93912070059196416'  # Skullgirls
CHANNEL_ID = '233106056086159363'  # region-assignment
# CHANNEL_ID = '257073315011624961'  # dev-test


# Roles
# Each role group contains roles which are mutually excusive, and contains a
# mapping from case-insensitive trigger keyword to role id
regions = [
    ('233093800506032128', ['na east', 'east coast']),
    ('233093905141202946', ['na central', 'midwest']),
    ('233093715231506432', ['na west', 'west coast']),
    ('233095632297000960', ['south america', 'brasil']),
    ('233095260471820288', ['europe east', 'eu east']),
    ('233095347197444106', ['europe west', 'eu west']),
    ('233095545852395522', ['asia east', 'japan']),
    ('233095608179621892', ['asia southeast']),
    ('233621433702416385', ['oceania', 'australia']),
]
roleGroups = [regions]
rolesById = {}


# Discord #
discordClient = discord.Client()


async def discord_task():
    await discordClient.login(discordToken, bot=True)
    await discordClient.connect()


@discordClient.event
async def on_message(message):
    if message.channel.id != CHANNEL_ID:
        return
    print('on_message:')

    text = message.content.lower()
    foundKeyphrase = False
    print(text)
    for roleGroup in roleGroups:
        selectedRoleId = find_keyphrase(roleGroup, text)
        if selectedRoleId is not None:
            foundKeyphrase = True
            groupRoleIds = [roleId for roleId, aliases in roleGroup]
            await reassign_role(
                message.author,
                selectedRoleId,
                groupRoleIds)

    reaction = '✅' if foundKeyphrase else '❌'
    await discordClient.add_reaction(message, reaction)


def find_keyphrase(roleGroup, text):
    for roleId, aliases in roleGroup:
        for keyphrase in aliases:
            if text.find(keyphrase) > -1:
                print('found:', keyphrase)
                return roleId
    return None


async def reassign_role(member, roleId, roleGroupIds):
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

    print('------')
    print('User: {0} ({1})'.format(
        discordClient.user.name,
        discordClient.user.id))
    print('Server: {0} ({1})'.format(
        discordClient.get_server(SERVER_ID),
        SERVER_ID))
    print('Channel: {0} ({1})'.format(
        discordClient.get_channel(CHANNEL_ID),
        CHANNEL_ID))
    print('------')

    rolesById = parse_roles(discordClient.get_server(SERVER_ID))


def parse_roles(server):
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
