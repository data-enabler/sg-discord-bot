import re

import discord

import client
import roles


# Constants
CHANNEL_ID = 233106056086159363  # role-assignment
# CHANNEL_ID = 257073315011624961  # dev-test


# Roles
# Each role group contains roles which are mutually excusive, and contains a
# mapping from case-insensitive trigger keyword to role id
regions = [
    (233093800506032128, ['na east', 'east coast']),
    (233093905141202946, ['na central', 'midwest']),
    (233093715231506432, ['na west', 'west coast']),
    (233095632297000960, ['south america', 'brasil']),
    (233095260471820288, ['europe east', 'eu east']),
    (233095347197444106, ['europe west', 'eu west']),
    (233095545852395522, ['asia east', 'japan', 'jp', '日本']),
    (233095608179621892, ['asia southeast']),
    (233621433702416385, ['oceania', 'australia']),
    (304317454581104643, ['other', 'undeclared', 'nowhere', 'africa', 'middle east']),
]
characters = [
    (269176765681893376, ['beo', 'beowulf']),
    (269176777962684416, ['big', 'big band', 'bigband', 'bb', 'band', 'brass', 'extend']),
    (269176664750030849, ['cer', 'cerebella', 'bella']),
    (269176793267699712, ['dou', 'double', 'dub', 'bomber']),
    (269176828877340672, ['eli', 'eliza']),
    (269176883076268033, ['fil', 'filia']),
    (269176708525981706, ['fuk', 'fukua']),
    (269176815308767242, ['msf', r'ms\. fortune', 'ms fortune', 'msfortune', r'(?<!robo( |-))fortune', 'fort']),
    (269176844832473088, ['pai', 'painwheel', 'pw']),
    (269176945621598208, ['par', 'parasoul', 'para']),
    (269176997320589312, ['pea', 'peacock']),
    (269177011996459009, ['rob', 'robo-fortune', 'robofortune', 'robo']),
    (269176751509209088, ['squ', 'squigly', 'squig']),
    (269176965590679552, ['val', 'valentine']),
    (None, ['nobody']),
]
roleGroups = [
    (regions, True),
    (characters, False),
]


async def on_ready():
    print('Listening for role assignment on channel #{0} ({1})'.format(
        client.discordClient.get_channel(CHANNEL_ID),
        CHANNEL_ID))


async def on_message(message: discord.Message):
    if message.channel.id != CHANNEL_ID:
        return

    text = message.content.lower()
    if text[0:2] == '//':
        return

    print('role-assignment: ', text)
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

    if foundKeyphrase:
        await roles.reassign_roles(
            message.author,
            netAdd,
            netRemove)

    reaction = '✅' if foundKeyphrase else '❌'
    await message.add_reaction(reaction)


def find_keyphrase(roleGroup, text):
    ids = []
    for roleId, aliases in roleGroup:
        for keyphrase in aliases:
            if re.search(r'\b' + keyphrase + r'\b', text):
                print('found:', keyphrase)
                ids.append(roleId)
    return ids
