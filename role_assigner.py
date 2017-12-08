import discord
import asyncio
import logging
import re

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
    ('233095545852395522', ['asia east', 'japan', 'jp', '日本']),
    ('233095608179621892', ['asia southeast']),
    ('233621433702416385', ['oceania', 'australia']),
    ('304317454581104643', ['other', 'undeclared', 'nowhere', 'africa', 'middle east']),
]
characters = [
    ('269176765681893376', ['beo', 'beowulf']),
    ('269176777962684416', ['big', 'big band', 'bigband', 'bb', 'band', 'brass', 'extend']),
    ('269176664750030849', ['cer', 'cerebella', 'bella']),
    ('269176793267699712', ['dou', 'double', 'dub', 'bomber']),
    ('269176828877340672', ['eli', 'eliza']),
    ('269176883076268033', ['fil', 'filia']),
    ('269176708525981706', ['fuk', 'fukua']),
    ('269176815308767242', ['msf', 'ms\. fortune', 'ms fortune', 'msfortune', '(?<!robo( |-))fortune', 'fort']),
    ('269176844832473088', ['pai', 'painwheel', 'pw']),
    ('269176945621598208', ['par', 'parasoul', 'para']),
    ('269176997320589312', ['pea', 'peacock']),
    ('269177011996459009', ['rob', 'robo-fortune', 'robofortune', 'robo']),
    ('269176751509209088', ['squ', 'squigly', 'squig']),
    ('269176965590679552', ['val', 'valentine']),
    (None, ['nobody']),
]
roleGroups = [
    (regions, True),
    (characters, False),
]
roleSentences = [
    ('388565602890940416', 'i have read and understand the rules\.?'),
]
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

    text = message.content.lower()
    if text[0:2] == '//':
        return

    print('on_message:', text)
    foundKeyphrase = False
    netAdd = set()
    netRemove = set()
    for roleGroup, exclusive in roleGroups:
        selectedRoleIds = find_keyphrase(roleGroup, text)
        if len(selectedRoleIds) == 0:
            continue
        foundKeyphrase = True

        groupRoleIds = set([roleId for roleId, aliases in roleGroup if roleId is not None])
        rolesToAdd = [r for r in selectedRoleIds if r is not None]
        rolesToAdd = set(rolesToAdd[:1] if exclusive else rolesToAdd)
        rolesToRemove = groupRoleIds - rolesToAdd

        netAdd |= rolesToAdd
        netRemove |= rolesToRemove

    for roleId, sentence in roleSentences:
        if re.search(r'^' + sentence + r'$', text):
            foundKeyphrase = True
            netAdd = set([roleId])


    if foundKeyphrase:
        await reassign_role(
            message.author,
            netAdd,
            netRemove)

    reaction = '✅' if foundKeyphrase else '❌'
    await discordClient.add_reaction(message, reaction)


def find_keyphrase(roleGroup, text):
    ids = []
    for roleId, aliases in roleGroup:
        for keyphrase in aliases:
            if re.search(r'\b' + keyphrase + r'\b', text):
                print('found:', keyphrase)
                ids.append(roleId)
    return ids


async def reassign_role(member, rolesToAdd, rolesToRemove):
    rolesToAdd = [rolesById[r] for r in rolesToAdd]
    rolesToRemove = [rolesById[r] for r in rolesToRemove]

    newRoles = [r for r in member.roles if r not in rolesToRemove]
    newRoles.extend(rolesToAdd)

    print('member:', member)
    print('adding:', [r.name for r in rolesToAdd])
    print('removing:', [r.name for r in rolesToRemove])
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
    # for i in rolesById:
    #     print(i, rolesById[i].name)


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
