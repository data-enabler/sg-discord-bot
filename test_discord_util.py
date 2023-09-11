import datetime
import unittest
from unittest.mock import MagicMock

import discord

from discord_util import (
    ModerationLogEntry,
    describe_moderation_action,
)


SAMPLE_USER = discord.User(
    state=MagicMock(),
    data={
        "id": 12345,
        "username": "datagram",
        "discriminator": "0",
        "avatar": None,
    },
)


class TestDescribeModerationAction(unittest.TestCase):
    def test_ban(self):
        entry = ModerationLogEntry(
            target=SAMPLE_USER,
            action=discord.AuditLogAction.ban,
            user=None,
            reason=None,
            created_at=datetime.datetime.now(),
        )
        self.assertEqual(describe_moderation_action(entry), 'banned')

    def test_timeout_no_time(self):
        entry = ModerationLogEntry(
            target=SAMPLE_USER,
            action=discord.AuditLogAction.member_update,
            user=None,
            reason=None,
            created_at=datetime.datetime.now(),
        )
        self.assertEqual(describe_moderation_action(entry), 'timed out')

    def test_timeout_with_time(self):
        t1 = datetime.datetime.now()

        t2 = datetime.datetime.now() + datetime.timedelta(days=10, hours=17)

        long_ago = datetime.datetime.fromtimestamp(0).isoformat()
        entry = ModerationLogEntry(
            target=discord.Member(
                state=MagicMock(),
                guild=MagicMock(),
                data={
                    "user": {
                        "id": 12345,
                        "username": "datagram",
                        "discriminator": "0",
                        "avatar": None,
                    },
                    "deaf": False,
                    "mute": False,
                    "joined_at": long_ago,
                    "roles": [],
                    "communication_disabled_until": t2.isoformat(),
                },
            ),
            action=discord.AuditLogAction.member_update,
            user=None,
            reason=None,
            created_at=t1,
        )
        self.assertEqual(
            describe_moderation_action(entry),
            'timed out for 10 days',
        )


if __name__ == '__main__':
    unittest.main()
