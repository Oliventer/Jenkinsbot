from discord.ext import commands
import datetime
import discord
from typing import Optional
import itertools

MAXIM_ID = 261952785602314252
AFK_CHANNEL = 731691971906633798


class BotCogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.storage = {}
        self.active_since = {}

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = member.guild.system_channel
        if channel is None:
            return
        if member.id == MAXIM_ID:
            msg = f'{member.mention}, пошел нахуй с канала.'
        else:
            msg = f'Привет-привет-привет-привет-привет-привет-привет, {member.mention}.'
        await channel.send(msg)

    @staticmethod
    def is_active(state):
        return not (state.self_mute or state.afk or state.channel is None)

    def get_voice_time(self, member):
        delta = datetime.datetime.now() - self.active_since[member.id]
        already_timed = self.storage.get(member.id, datetime.timedelta())
        self.storage[member.id] = already_timed + delta

        print(self.storage[member.id].total_seconds())

    def get_members(self):
        members = itertools.chain.from_iterable \
        ([channel.members for channel in self.bot.get_all_channels() if isinstance(channel, discord.VoiceChannel)])
        return members

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not self.is_active(before) and self.is_active(after):
            self.active_since[member.id] = datetime.datetime.now()
        elif self.is_active(before) and not self.is_active(after):
            self.get_voice_time(member)

    @commands.Cog.listener()
    async def on_ready(self):
        members = self.get_members()
        for member in members:
            if self.is_active(member.voice):
                self.active_since[member.id] = datetime.datetime.now()
        print("Hello!")

    @commands.command()
    async def ping(self, ctx):
        write = []
        members = self.get_members()
        for member in members:
            if self.is_active(member.voice):
                self.get_voice_time(member)
                self.active_since[member.id] = datetime.datetime.now()
                write.append(f'{str(member)}: {self.storage[member.id]}')
        for values in range(len(write)):
            await ctx.send(write[values])


def setup(bot):
    bot.add_cog(BotCogs(bot))
