import datetime
import re
import textwrap
from typing import Optional, Union, cast

import discord
import nuclino
import nuclino.objects

import constants
from discord_util import (
    ModerationLogEntry,
    print_user,
    describe_moderation_action,
)
from nuclino_api import create_nuclino_item, find_nuclino_item

# Discord
CHANNEL_ID = 1019958027807359018  # mod-coordination
# CHANNEL_ID = 1027785307858407424  # forum-test

# Nuclino
WORKSPACE_ID = "22ddcaf7-2604-41dc-a21a-54d8ea1932a9"  # General
CLUSTER_ID = "5724f725-450d-a781-9d4b-9ba43b7cbe17"  # Action Log
# CLUSTER_ID = "164c42bd-f688-42c4-9920-aebe40bfa409"  # test
THREAD_REGEX = re.compile(r"^\[Discord Thread ID: (\d+)")


intents = {
    "bans",  # discord.Intents.bans
    "guild_messages",  # discord.Intents.guild_messages
    "guilds",  # discord.Intents.guilds
    "members",  # discord.Intents.members
}


def init(discord_client: discord.Client, nuclino_client: nuclino.Nuclino):
    async def on_ready():
        output_channel = get_output_channel(discord_client)
        # Make sure ID is good
        get_server(discord_client)

        print("Logging moderation actions to #{0} ({1})".format(
            output_channel,
            output_channel.id))

    async def on_raw_member_remove(payload: discord.RawMemberRemoveEvent):
        if (payload.guild_id != constants.SERVER_ID):
            return

        entry = await get_audit_event(
            discord_client,
            {discord.AuditLogAction.kick, discord.AuditLogAction.ban},
            payload.user,
        )
        if entry is None:
            # User may have left on their own
            return

        await log_moderation_event(
            entry,
            nuclino_client,
            get_output_channel(discord_client),
            get_server(discord_client),
        )

    async def on_member_update(before: discord.Member, after: discord.Member):
        if (after.guild.id != constants.SERVER_ID):
            return

        if before.is_timed_out() or not after.is_timed_out():
            # We're only interested in timeout actions
            return

        entry = await get_audit_event(
            discord_client,
            {discord.AuditLogAction.member_update},
            after,
        )
        if entry is None:
            print("Audit log entry not found for timed out user {0}"
                  .format(print_user(after)))
            return

        await log_moderation_event(
            entry,
            nuclino_client,
            get_output_channel(discord_client),
            after.guild,
        )

    async def on_member_unban(guild: discord.Guild, user: discord.User):
        if (guild.id != constants.SERVER_ID):
            return

        entry = await get_audit_event(
            discord_client,
            {discord.AuditLogAction.unban},
            user,
        )
        if entry is None:
            print("Audit log entry not found for unbanned user {0}"
                  .format(print_user(user)))
            return

        await log_moderation_event(
            entry,
            nuclino_client,
            get_output_channel(discord_client),
            guild,
        )

    return {
        on_ready,
        on_raw_member_remove,
        on_member_update,
        on_member_unban,
    }


def get_output_channel(client: discord.Client) -> discord.ForumChannel:
    channel = cast(
        Optional[Union[
            discord.abc.GuildChannel,
            discord.Thread,
            discord.DMChannel,
            discord.GroupChannel,
        ]],
        client.get_channel(CHANNEL_ID),
    )
    assert channel is not None
    assert channel.type is discord.ChannelType.forum
    return cast(discord.ForumChannel, channel)


def get_server(client: discord.Client) -> discord.Guild:
    guild: Optional[discord.Guild] = client.get_guild(constants.SERVER_ID)
    assert guild is not None
    return guild


async def get_audit_event(
    discord_client: discord.Client,
    actionTypes: set[discord.AuditLogAction],
    target: discord.abc.User,
) -> Optional[ModerationLogEntry]:
    guild = get_server(discord_client)
    one_minute_ago = discord.utils.utcnow() - datetime.timedelta(minutes=1)
    logs: list[discord.AuditLogEntry] = [
        entry
        async for entry
        in guild.audit_logs(limit=10)
        if entry.target == target
        and entry.action in actionTypes
        and entry.created_at > one_minute_ago
    ]
    if len(logs) == 0:
        return None
    return ModerationLogEntry.from_audit_log_entry(logs[0])


async def log_moderation_event(
    entry: ModerationLogEntry,
    nuclino_client: nuclino.Nuclino,
    channel: discord.ForumChannel,
    guild: discord.Guild,
):
    action_description = describe_moderation_action(entry)
    print("{user} was {past_tense_action} by {moderator}".format(
        user=print_user(entry.target),
        past_tense_action=action_description,
        moderator=print_user(entry.user),
    ))
    nuclino_item = await get_or_create_nuclino_item(nuclino_client, entry)
    thread_id = get_discord_thread_id(nuclino_item)
    target = entry.target
    message = textwrap.dedent("""\
        {user} was {past_tense_action} by {moderator}

        Reason: {reason}\
        """.format(
            user=f"{target.name}#{target.discriminator}({target.mention})",
            past_tense_action=action_description,
            reason=entry.reason or "`No reason given`",
            moderator=entry.user.mention if entry.user else "unknown",
        ))

    if thread_id is None:
        initial_message = f"""\
{nuclino_item.url}
User ID: {entry.target.id}

{message}\
"""
        thread = (await channel.create_thread(
            name=f"{entry.target.name}({entry.target.discriminator})",
            content=initial_message,
        )).thread
        nuclino_item.update(
            content="[Discord Thread ID: {thread_id}]({url})\n\n{orig}".format(
                thread_id=thread.id,
                url=thread.jump_url,
                orig=nuclino_item.content,
            )
        )
    else:
        thread = cast(discord.Thread, await guild.fetch_channel(thread_id))
        if thread is None:
            print(f"Unable to find thread with id {thread_id}")
        else:
            await thread.send(message)


async def get_or_create_nuclino_item(
    nuclino_client: nuclino.Nuclino,
    entry: ModerationLogEntry,
) -> nuclino.objects.Item:
    target: Union[discord.User, discord.Member] = entry.target
    entryDate: datetime.datetime = entry.created_at
    update = textwrap.dedent("""\
        ## Status: {status}

        {reason}\\
        ―{moderator} {date}\
        """.format(
            status=describe_moderation_action(entry),
            reason=entry.reason or "[No reason given]",
            moderator=print_user(entry.user),
            date=entryDate.strftime("%Y/%m/%d"),
        ),
    )

    item = await find_nuclino_item(
        nuclino_client=nuclino_client,
        workspace_id=WORKSPACE_ID,
        text=str(target.id),
    )
    if item is None:
        content = "User ID: {user_id}\n\n{update}".format(
            user_id=target.id,
            update=update,
        )
        return await create_nuclino_item(
            nuclino_client=nuclino_client,
            parent_id=CLUSTER_ID,
            title="{0}#{1}".format(target.name, target.discriminator),
            content=content,
        )
    else:
        new_content = "{orig_content}\n---\n\n{update}".format(
            orig_content=item.content,
            update=update,
        )
        return item.update(content=new_content)


def get_discord_thread_id(nuclino_item: nuclino.objects.Item) -> Optional[int]:
    match = THREAD_REGEX.match(cast(str, nuclino_item.content))
    return match and int(match.group(1))
