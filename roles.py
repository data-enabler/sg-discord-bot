import sys
from typing import Set, Dict

import discord

import client
import constants


rolesById: Dict[int, discord.Role] = {}


async def on_ready():
    server = client.discordClient.get_guild(constants.SERVER_ID)
    if not server:
        return
    global rolesById
    rolesById = enumerate_roles(server)


def enumerate_roles(server: discord.Guild) -> Dict[int, discord.Role]:
    rolesById = {role.id: role for role in server.roles}
    if len(rolesById) == 0:
        sys.exit('Unable to fetch roles, exiting')
    print('Server roles:')
    for i in rolesById:
        print(i, rolesById[i].name)
    return rolesById


async def reassign_roles(member: discord.Member, rolesToAdd: Set[int], rolesToRemove: Set[int]):
    rolesToAdd = [rolesById[r] for r in rolesToAdd]
    rolesToRemove = [rolesById[r] for r in rolesToRemove]

    newRoles = [r for r in member.roles if r not in rolesToRemove]
    newRoles.extend(rolesToAdd)

    print('member:', member)
    print('adding:', [r.name for r in rolesToAdd])
    print('removing:', [r.name for r in rolesToRemove])
    print('new roles:', [r.name for r in newRoles])

    await member.edit(roles=newRoles)
