import os

import discord

client = discord.Client()

TOKEN = os.getenv("DISCORD_TOKEN")


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    await message.channel.send("Hola has enviado un mensaje")


client.run(TOKEN)
