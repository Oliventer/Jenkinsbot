from discord.ext import commands, tasks
import discord
from itertools import chain
import os
from const import SPECIAL_EMOJIS, MY_ID, DEFAULT_EMOJI, SAVE_FILENAME
from time_storage import TimeStorage
from datetime import datetime
import asyncio


def tabulate(n):
    return "\u200B\t" * n


def get_special_emoji(member):
    return SPECIAL_EMOJIS.get(member.id, DEFAULT_EMOJI)


def prepare_emoji_list(members):
    first, *rest = members
    emoji_key = 'me_as_top_1' if first.id == MY_ID else 'not_me_as_top_1'
    first_emoji = SPECIAL_EMOJIS[emoji_key]
    rest_emojis = list(map(get_special_emoji, rest))
    return [first_emoji, *rest_emojis]


def format_time(time_delta):
    total_seconds = int(time_delta.total_seconds())
    hours, remainder = divmod(total_seconds, 60 * 60)
    minutes, seconds = divmod(remainder, 60)
    return f'{hours:02}:{minutes:02}:{seconds:02}'


class BotCogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.time_storage = self.create_time_storage_instance()
        self.daily_restart.start()

    @staticmethod
    def create_time_storage_instance():
        if os.path.isfile(SAVE_FILENAME):
            loop = asyncio.get_event_loop()
            result = loop.run_until_complete(TimeStorage.from_db(SAVE_FILENAME))
            return result
        return TimeStorage(SAVE_FILENAME)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = member.guild.system_channel
        if channel is None:
            return
        else:
            msg = f'Привет-привет-привет-привет-привет-привет-привет, {member.mention}.'
        await channel.send(msg)

    @staticmethod
    def is_active(state):
        return not (state.self_mute or state.afk or state.channel is None)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not self.is_active(before) and self.is_active(after):
            self.time_storage.start_session(member.id)
        elif self.is_active(before) and not self.is_active(after):
            self.time_storage.end_session(member.id)

    def start_members_sessions(self):
        voice_channels = chain.from_iterable(guild.voice_channels for guild in self.bot.guilds)
        members = chain.from_iterable(vc.members for vc in voice_channels)
        active_members = filter(lambda m: self.is_active(m.voice), members)
        for member in active_members:
            self.time_storage.start_session(member.id)

    @commands.Cog.listener()
    async def on_ready(self):
        self.start_members_sessions()
        print("Hello!")

    @tasks.loop(hours=23 - datetime.now().hour, minutes=60 - datetime.now().minute, seconds=60 - datetime.now().second)
    async def daily_restart(self):
        if self.daily_restart.current_loop == 0:
            self.daily_restart.change_interval(hours=24)
            return
        self.time_storage.wipe_storage()
        self.start_members_sessions()
        print(f'Wipe time: {datetime.now()}')

    def cog_unload(self):
        self.daily_restart.cancel()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.time_storage.save())

    @commands.command()
    async def ping(self, ctx):
        members = list(map(ctx.guild.get_member, self.time_storage.get_top_member_ids(5)))
        if not members:
            await ctx.send('У тебя нет друзей :(, по крайней мере пока что.')
            return
        emojis = prepare_emoji_list(members)
        embed = discord.Embed(title="Список работяг:", colour=0x7FDBFF)
        for member, emoji in zip(members, emojis):
            member_time = self.time_storage.total_time(member.id)
            embed.add_field(name=f'{emoji} {member}:',
                            value=f'{tabulate(8)}{format_time(member_time)}',
                            inline=False)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(BotCogs(bot))
