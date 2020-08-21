from config import token
from discord.ext import commands
from const import STEPAN_ID, EUROPE_MEME_CHANNEL_ID


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='$')
        self.load_extension('time_counter')

    def run(self):
        super().run(token, reconnect=True)

    async def on_message(self, message):
        author = message.author
        if author.bot:
            return
        channel = message.channel
        if author.id == STEPAN_ID and channel.id == EUROPE_MEME_CHANNEL_ID:
            await channel.send(f'прошу прощение за то что {author.mention} насрал здесь! извините.')
        elif channel.id == EUROPE_MEME_CHANNEL_ID:
            await channel.send(f'{author.mention}, кек.')
        await self.process_commands(message)

    async def close(self):
        await bot.cogs['BotCogs'].time_storage.save()
        self.unload_extension('time_counter')
        await super().close()


if __name__ == '__main__':
    bot = Bot()
    bot.run()
