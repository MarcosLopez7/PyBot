import os

import discord

client = discord.Client()

TOKEN = os.getenv("DISCORD_TOKEN")


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

client.run(TOKEN)
