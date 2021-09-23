import os
import discord

from DBManager import DBManager

client = discord.Client()

TOKEN = os.getenv("DISCORD_TOKEN")

db_manager = DBManager()
conn = db_manager.get_conn()


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


@client.event
async def on_message(message):
    if message.content == '$set_welcome_channel':
        roles = message.author.roles

        for role in roles:
            if role.permissions.administrator:
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT * FROM EspecialChannel WHERE type = %s
                    """,
                    ('welcome',)
                )

                result = cursor.fetchall()

                if not result:
                    cursor.execute("""
                        INSERT INTO EspecialChannel (guild_id,channel_id,type,name) VALUES (
                            %s,%s,%s,%s
                        )
                    """, (message.guild.id, message.channel.id, 'welcome', message.channel.name))

                    conn.commit()
                else:
                    id_especial_channel = result[0][0]

                    cursor.execute("""
                        UPDATE EspecialChannel
                        SET guild_id = %s,
                            channel_id = %s,
                            name = %s
                        WHERE
                            id = %s
                    """, (message.guild.id, message.channel.id, message.channel.name, id_especial_channel))

                    conn.commit()

                await message.channel.send("Channel has been set as welcome channel")
                break


client.run(TOKEN)
