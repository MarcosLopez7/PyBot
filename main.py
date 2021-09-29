import os
import discord

from DBManager import DBManager

intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)

TOKEN = os.getenv("DISCORD_TOKEN")

db_manager = DBManager()
conn = db_manager.get_conn()


def is_admin_member(member):
    roles = member.roles

    for role in roles:
        if role.permissions.administrator:
            return True

    return False


def query_especial_channel(type_channel):
    cursor = conn.cursor()

    cursor.execute("""
                            SELECT id FROM EspecialChannel WHERE type = %s
                            """,
                   (type_channel,)
                   )

    result = cursor.fetchall()

    return result


def set_cmd(cmd, message):
    if is_admin_member(message.author):
        cursor = conn.cursor()
        type_channel = 'welcome' if cmd == '$set_welcome_channel' else 'rule'
        result = query_especial_channel(type_channel)

        if not result:
            query = """
                                INSERT INTO EspecialChannel (guild_id,channel_id,type,name) VALUES (
                                    %s,%s,%s,%s
                                    )
                                """
            parameters = (message.guild.id, message.channel.id, type_channel, message.channel.name)
        else:
            query = """
                    UPDATE EspecialChannel
                    SET guild_id = %s,
                        channel_id = %s,
                        name = %s
                    WHERE
                        id = %s
                """
            parameters = (message.guild.id, message.channel.id, message.channel.name, result[0][0])

        cursor.execute(query, parameters)
        conn.commit()

        return f"Channel has been set as {type_channel} channel"


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


@client.event
async def on_member_join(member):
    print("Hola un nuevo miembro se ha unido")
    cursor = conn.cursor()
    cursor.execute("""SELECT channel_id FROM EspecialChannel WHERE type = %s""", ('welcome',))
    result = cursor.fetchone()

    channel = member.guild.get_channel(int(result[0]))

    await channel.send(f"Bienvenido al canal {member.mention}")


@client.event
async def on_message(message):
    if message.content.startswith("$") and len(message.content.split(" ")) == 1:
        await message.channel.send(set_cmd(message.content, message))


client.run(TOKEN)
