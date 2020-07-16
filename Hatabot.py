import discord
import json
from config import token
from discord.ext import commands

STEPAN_ID = 378318866524143627
GUILD_ID = 545315019982897162
CHANNEL_ID = 719279953962598401


class PahanBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='^')
        self.load_extension("Hatacogs")
        self.token = token

    def run(self):
        super().run(self.token, reconnect=True)

    async def on_message(self, message):
        author = message.author
        if author.bot:
            return
        channel = message.channel
        if author.id == STEPAN_ID and channel.id == CHANNEL_ID:
            await channel.send(f'прошу прощение за то что {author.mention} насрал здесь! извините.')
        elif channel.id == CHANNEL_ID:
            await channel.send(f'{author.mention}, кек.')


"""@bot.command()
async def write(ctx, arg):
    await ctx.send(arg)"""


if __name__ == '__main__':
    pahan = PahanBot()
    pahan.run()
