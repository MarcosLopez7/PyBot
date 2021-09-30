import os,re
import pandas as pd
import discord

from sqlalchemy import create_engine

from DBManager import DBManager

intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)

TOKEN = os.getenv("DISCORD_TOKEN")

db_manager = DBManager()
conn = db_manager.get_conn()

engine = create_engine(f'postgresql+psycopg2://{os.getenv("POSTGRES_USER")}:{os.getenv("POSTGRES_PASSWORD")}@localhost:5432/{os.getenv("POSTGRES_DB")}')

bad_words_df = pd.read_csv('bad_words.csv')


def check_if_user_ban(member):
    cursor = conn.cursor()

    query = """
           SELECT SUM(point) FROM Reports WHERE discord_user_id = %s
        """

    cursor.execute(query, (str(member.id),))

    result = cursor.fetchone()

    return result[0] >= 10


def report_user_by_bad_words(member):
    cursor = conn.cursor()

    query = """
        INSERT INTO Reports (discord_user_id, title, description, point, guild_id) VALUES (%s,%s,%s,%s,%s)
    """

    parameters = (member.id, "Bad Word Use", "Bad Word Use", 1, str(member.guild.id))

    cursor.execute(query, parameters)
    conn.commit()

    # check_if_user_ban(member)


def has_text_bad_words(text):
    result = bad_words_df['word'].apply(
        lambda word: True if re.search(f'(\\W|^){word.lower()}(\\W|$)', text) else False
    )
    return sum(result) > 0


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


def query_default_role():
    cursor = conn.cursor()

    cursor.execute("""SELECT id FROM Roles WHERE is_default""")

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

    cursor.execute("""SELECT role_id FROM Roles WHERE is_default""")
    result = cursor.fetchone()
    role = member.guild.get_role(int(result[0]))

    await member.add_roles(role)

    await channel.send(f"Bienvenido al canal {member.mention}")


@client.event
async def on_message(message):
    if message.content.startswith("$") and len(message.content.split(" ")) == 1:
        await message.channel.send(set_cmd(message.content, message))
    elif message.content.startswith("$") and len(message.role_mentions) == 1:
        if is_admin_member(message.author):
            result = query_default_role()
            role = message.role_mentions[0]
            cursor = conn.cursor()
            if not result:
                query = """
                            INSERT INTO Roles (name,is_default,role_id) VALUES (%s,%s,%s)
                        """
                parameters = (role.name, True, role.id)
            else:
                query = """
                                            UPDATE Roles 
                                            SET name = %s,
                                            role_id = %s
                                            WHERE id = %s
                        """
                parameters = (role.name, role.id, result[0][0])

            cursor.execute(query, parameters)

            conn.commit()

            await message.channel.send(f"Role {role.name} has been set as default role")
    else:
        if has_text_bad_words(message.content.lower()):
            await message.delete()
            report_user_by_bad_words(message.author)
            await message.channel.send("Oye, esto tiene una mala palabra, ten mas cuidado")
            if check_if_user_ban(message.author):
                await message.author.ban()

client.run(TOKEN)
