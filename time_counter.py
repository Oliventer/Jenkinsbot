from discord.ext import commands
from datetime import datetime
import discord
from typing import Optional
import itertools
import os
import json
from main import STEPAN_ID

MAXIM_ID = 261952785602314252
AFK_CHANNEL = 731691971906633798
MY_ID = 173139208532131841


class BotCogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.storage = {}
        self.active_since = {}
        self.emoji_storage = {}

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
        if state is not None:
            return not (state.self_mute or state.afk or state.channel is None)

    def get_voice_time(self, member):
        delta = datetime.now() - self.active_since[member.id]
        already_timed = self.bot.storage.get(member.id, datetime.min)
        self.bot.storage[member.id] = already_timed + delta

    def get_members(self):
        members = itertools.chain.from_iterable \
        ([channel.members for channel in self.bot.get_all_channels() if isinstance(channel, discord.VoiceChannel)])
        return members

    def get_dict_members(self):
        members = []
        for guild in self.bot.guilds:
            sorted_records = sorted(self.bot.storage.items(), key=lambda item: item[1], reverse=True)
            for member in sorted_records:
                members.append(guild.get_member(member[0]))
        return members

    @staticmethod
    def empty_space_fill(count):
        return "\u200B\t" * count

    def get_emoji(self, members):
        top = 0
        for member in members:
            top += 1
            if member.id == MY_ID and top == 1:
                self.emoji_storage[MY_ID] = '\U0001f4aa'
            elif member.id != MY_ID and top == 1:
                self.emoji_storage[member.id] = '\U0001f921'
            else:
                self.emoji_storage[member.id] = '\U0001f476'
            if member.id == STEPAN_ID:
                self.emoji_storage[member.id] = '\U0001f412'
        print(self.emoji_storage)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not self.is_active(before) and self.is_active(after):
            self.active_since[member.id] = datetime.now()
        elif self.is_active(before) and not self.is_active(after):
            self.get_voice_time(member)

    def open_config(self):
        with open('total_time.json', encoding='utf-8') as f:
            cfg = json.load(f)
            for key in cfg:
                key = int(key)
                time_obj = cfg[str(key)]
                value = datetime.fromisoformat(time_obj)
                self.bot.storage[key] = value

    @commands.Cog.listener()
    async def on_ready(self):
        if os.path.isfile('total_time.json'):
            self.open_config()
        members = self.get_members()
        for member in members:
            if self.is_active(member.voice):
                self.active_since[member.id] = datetime.now()
        print("Hello!")

    def cog_unload(self):
        members = self.get_dict_members()
        for member in members:
            if self.is_active(member.voice):
                self.get_voice_time(member)

    @commands.command()
    async def ping(self, ctx):
        members = self.get_dict_members()
        self.get_emoji(members)
        embed_obj = discord.Embed(title="Список работяг:", colour=0x7FDBFF)
        for member in members:
            if self.is_active(member.voice):
                self.get_voice_time(member)
                self.active_since[member.id] = datetime.now()
            embed_obj.add_field(name=f'{self.emoji_storage[member.id]}  **{member}**:',
                                value=f'{self.empty_space_fill(8)}{self.bot.storage[member.id].strftime("%H:%M:%S")}',
                                inline=False)
        await ctx.send(embed=embed_obj)


def setup(bot):
    bot.add_cog(BotCogs(bot))
