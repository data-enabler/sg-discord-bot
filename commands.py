import textwrap
from typing import Optional, Union, cast

import discord
from discord.ext import commands

REPORTS_CHANNEL_ID = 866439107030548540  # reports
# REPORTS_CHANNEL_ID = 257073315011624961  # dev-test


intents = {
    "guilds",  # discord.Intents.guilds
    "members",  # discord.Intents.members
    "guild_messages",  # discord.Intents.guild_messages
    "message_content",  # discord.Intents.message_content
}


def init(discord_client: commands.Bot):
    async def on_ready():
        reports_channel = get_reports_channel(discord_client)
        print('Sending moderation reports to channel #{0} ({1})'.format(
            reports_channel,
            reports_channel.id))

    @discord_client.command()
    async def moderators(
        ctx: commands.Context,
        member: Optional[discord.Member] = None,
        details: str = ''
    ):
        """Request moderator assistance."""
        channel = cast(discord.TextChannel, ctx.channel)
        last_member_messages = None
        if member:
            contents = [
                quote(m.content)
                async for m in channel.history(limit=30)
                if m.author == member
                and m.content
            ][:3]
            last_member_messages = '\n---\n'.join(list(contents))

        report = textwrap.dedent('''\
            [User moderation report]
            Reporter: {reporter}
            Channel: {channel}
            Member: {member}
            Details: {details}\
            '''.format(
                reporter=ctx.author.mention,
                channel=channel.mention,
                member=member and member.mention,
                details=details and '`' + details + '`' or None,
            ))
        if last_member_messages:
            report += ('\nLatest messages from member in channel:\n'
                       + last_member_messages)
        print(report)
        reports_channel = get_reports_channel(discord_client)
        await reports_channel.send(report)
        await ctx.send(
            'Thanks for the report! One of our moderators will take a look as soon as possible.',
        )

    return {
        on_ready
    }


def get_reports_channel(client: discord.Client) -> discord.TextChannel:
    channel = cast(
        Optional[Union[
            discord.abc.GuildChannel,
            discord.Thread,
            discord.DMChannel,
            discord.GroupChannel,
        ]],
        client.get_channel(REPORTS_CHANNEL_ID),
    )
    assert channel is not None
    assert channel.type is discord.ChannelType.text
    return cast(discord.TextChannel, channel)


def quote(str: str):
    return textwrap.indent(str, '> ', lambda line: True)
