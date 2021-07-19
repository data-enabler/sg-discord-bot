import itertools
import textwrap

import discord
from discord_slash import SlashCommand, SlashContext

import client
import constants

REPORTS_CHANNEL_ID = 866439107030548540  # reports
# REPORTS_CHANNEL_ID = 257073315011624961  # dev-test

slash = SlashCommand(client.discordClient, sync_commands=True)
reports_channel = None

async def on_ready():
    global reports_channel
    reports_channel = client.discordClient.get_channel(REPORTS_CHANNEL_ID)
    print('Sending moderation reports to channel #{0} ({1})'.format(
        reports_channel,
        REPORTS_CHANNEL_ID))

@slash.slash(
    name='moderators',
    guild_ids=[constants.SERVER_ID],
)
async def moderators(ctx: SlashContext, member: discord.Member = None, details=''):
    """Request moderator assistance."""
    last_member_messages = None
    if member:
        messages = await ctx.channel.history(limit=30).flatten()
        messages = filter(lambda m: m.author == member, messages)
        messages = filter(lambda m: m.content, messages)
        messages = itertools.islice(messages, 3)
        contents = map(lambda m: m.content, messages)
        contents = map(quote, contents)
        last_member_messages = '\n---\n'.join(list(contents))

    report = textwrap.dedent('''\
        [User moderation report]
        Reporter: {reporter}
        Channel: {channel}
        Member: {member}
        Details: {details}\
        '''.format(
            reporter=ctx.author.mention,
            channel=ctx.channel.mention,
            member=member and member.mention,
            details=details and '`' + details + '`' or None,
        ))
    if last_member_messages:
        report += '\nLatest messages from member in channel:\n' + last_member_messages
    print(report)
    reports_channel and await reports_channel.send(report)
    await ctx.send(
        'Thanks for the report! One of our moderators will take a look as soon as possible.',
        hidden=True,
    )

def quote(str: str):
    return textwrap.indent(str, '> ', lambda line: True)
