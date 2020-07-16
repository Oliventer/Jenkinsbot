from discord.ext import commands
import datetime
import discord
from typing import Optional

MAXIM_ID = 261952785602314252


def is_active(state):
    return state.self_mute or state.afk or state.channel is None


class StepanTrolling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.storage = {}
        self.active_since = {}

    def get_current_delta(self, member: discord.Member) -> Optional[datetime.timedelta]:
        return self.bot.storage.get(member.id)

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

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if is_active(before) and not is_active(after):
            self.active_since[member.id] = datetime.datetime.now()
        elif not is_active(before) and is_active(after):
            delta = datetime.datetime.now() - self.active_since[member.id]
            current_delta = self.storage.get(member.id)
            if current_delta is None:
                self.storage[member.id] = datetime.timedelta()
            self.storage[member.id] += delta

            print(self.storage[member.id].total_seconds())


def setup(bot):
    bot.add_cog(StepanTrolling(bot))
