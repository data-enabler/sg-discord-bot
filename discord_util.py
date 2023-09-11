from __future__ import annotations
from dataclasses import dataclass
import datetime
from typing import Literal, Optional, Union, cast

import discord
import humanize


ACTION_PAST_TENSE_MAP = {
    discord.AuditLogAction.ban: "banned",
    discord.AuditLogAction.unban: "unbanned",
    discord.AuditLogAction.kick: "kicked",
    discord.AuditLogAction.member_update: "timed out",
}


@dataclass
class ModerationLogEntry:
    target: Union[discord.User, discord.Member]
    action: Literal[
        discord.AuditLogAction.ban,
        discord.AuditLogAction.unban,
        discord.AuditLogAction.kick,
        discord.AuditLogAction.member_update,
    ]
    user: Optional[Union[discord.User, discord.Member]]
    reason: Optional[str]
    created_at: datetime.datetime

    @staticmethod
    def from_audit_log_entry(
        entry: discord.AuditLogEntry,
    ) -> ModerationLogEntry:
        assert entry.action in [
            discord.AuditLogAction.ban,
            discord.AuditLogAction.unban,
            discord.AuditLogAction.kick,
            discord.AuditLogAction.member_update,
        ]
        assert (isinstance(entry.target, discord.User)
                or isinstance(entry.target, discord.Member))
        return ModerationLogEntry(
            target=entry.target,
            action=entry.action,  # type: ignore
            user=entry.user,
            reason=entry.reason,
            created_at=entry.created_at,
        )


def print_user(user: Optional[discord.abc.User]) -> str:
    if user is None:
        return "unknown"
    return "{0}#{1}({2})".format(
        user.name,
        user.discriminator,
        user.id,
    )


def describe_moderation_action(entry: ModerationLogEntry) -> str:
    action = entry.action
    target = entry.target
    is_timeout_event = action == discord.AuditLogAction.member_update
    if is_timeout_event:
        if isinstance(target, discord.Member) and target.timed_out_until:
            return "timed out for " + humanize.naturaldelta(
                target.timed_out_until - entry.created_at
            )
        else:
            return "timed out"
    else:
        return ACTION_PAST_TENSE_MAP[action]
