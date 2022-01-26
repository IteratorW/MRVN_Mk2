import logging

import coloredlogs
import discord

from impl import env

client = discord.Client()

coloredlogs.install(fmt="[%(asctime)s] [%(name)s/%(levelname)s]: %(message)s", datefmt="%H:%M:%S",
                    field_styles={"levelname": {"color": "blue"}, "message": {"color": "white", "bright": True}})
logging.basicConfig(level=logging.INFO if not env.debug else logging.DEBUG)


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

client.run(env.token)
