from typing import Literal, Optional, Union, cast
import discord


class ModerationLogEntry(discord.AuditLogEntry):
    target: Union[discord.User, discord.Member]
    action: Literal[
        discord.AuditLogAction.ban,
        discord.AuditLogAction.unban,
        discord.AuditLogAction.kick,
        discord.AuditLogAction.member_update,
    ]


def assertIsModerationLogEntry(
    entry: discord.AuditLogEntry
) -> ModerationLogEntry:
    assert entry.action in [
        discord.AuditLogAction.ban,
        discord.AuditLogAction.unban,
        discord.AuditLogAction.kick,
        discord.AuditLogAction.member_update,
    ]
    return cast(ModerationLogEntry, entry)


def print_user(user: Optional[discord.abc.User]) -> str:
    if user is None:
        return "unknown"
    return "{0}#{1}({2})".format(
        user.name,
        user.discriminator,
        user.id,
    )
