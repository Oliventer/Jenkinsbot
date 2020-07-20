from discord.ext import commands
from datetime import datetime
import discord
from typing import Optional
import itertools
import os
import json

MAXIM_ID = 261952785602314252
AFK_CHANNEL = 731691971906633798


class BotCogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.storage = {}
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

            print(self.bot.storage)

    @commands.Cog.listener()
    async def on_ready(self):
        if os.path.isfile('total_time.json'):
            self.open_config()
        members = self.get_members()
        for member in members:
            if self.is_active(member.voice):
                self.active_since[member.id] = datetime.now()
                print(self.active_since[member.id].strftime("%H:%M:%S"))
        # self.get_dict_members()
        print("Hello!")

    def cog_unload(self):
        members = self.get_dict_members()
        for member in members:
            if self.is_active(member.voice):
                self.get_voice_time(member)

    @commands.command()
    async def ping(self, ctx):
        write = ""
        members = self.get_dict_members()
        for member in members:
            if self.is_active(member.voice):
                self.get_voice_time(member)
                self.active_since[member.id] = datetime.now()
            write += f'\U0001f476 {str(member)}: {self.bot.storage[member.id].strftime("%H:%M:%S")}\n'
        embed_obj = discord.Embed(description=write, title="Список работяг:", colour=0x7FDBFF)
        await ctx.send(embed=embed_obj)


def setup(bot):
    bot.add_cog(BotCogs(bot))
