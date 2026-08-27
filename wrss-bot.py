import discord
import traceback
import logging
import re
import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

THREAD_NAME_MAX_LEN = 100


async def new_message_handler(message):
    if message.author == client.user or message.guild is None:
        return
    thread_created = False
    if message.position is None:
        try:
            thread_created = await thread_handler(message)
        except Exception:
            logging.error(traceback.format_exc())
        try:
            await message.add_reaction(settings.seen_emoji_long_id)
        except Exception:
            logging.error(traceback.format_exc())
    elif get_thread_name(message.content) == "[cd]":
        try:
            await message.add_reaction(settings.seen_emoji_long_id)
        except Exception:
            logging.error(traceback.format_exc())
    try:
        await doodle_handler(message)
    except Exception:
        logging.error(traceback.format_exc())
    try:
        await poll_handler(message)
    except Exception:
        logging.error(traceback.format_exc())
    if thread_created:
        try:
            fresh = await message.channel.fetch_message(message.id)
            await update_reaction_msg(fresh)
        except Exception:
            logging.error(traceback.format_exc())


async def resolve_channel(channel_id):
    channel = client.get_channel(channel_id)
    if channel is not None:
        return channel
    try:
        return await client.fetch_channel(channel_id)
    except (discord.NotFound, discord.Forbidden, discord.HTTPException):
        logging.error("Could not resolve channel %s", channel_id)
        return None


async def doodle_handler(message):
    if message.channel.id == settings.doodle_channel_id:
        return
    if not any(link in message.content for link in settings.doodle_links):
        return
    channel = await resolve_channel(settings.doodle_channel_id)
    if channel is None:
        return
    new_message = await channel.send(message.jump_url + "\n>>> " + message.content)
    await new_message.add_reaction(settings.doodle_seen_reaction)


async def poll_handler(message):
    options = re.findall(r"> - .+", message.content)
    for option in options:
        emoji = get_option_emoji(option)
        if emoji is None:
            continue
        try:
            await message.add_reaction(emoji)
        except discord.HTTPException:
            logging.error("Could not add poll reaction %r", emoji)


def get_option_emoji(option_string):
    parts = option_string[4:].split()
    if not parts:
        return None
    emoji = parts[0]
    if len(emoji) >= 2 and emoji[0] == "<" and emoji[-1] == ">":
        emoji = emoji[1:-1]
    return emoji or None


async def thread_handler(message):
    thread_name = get_thread_name(message.content)
    if thread_name is None or thread_name == "[]":
        return False
    thread = await message.create_thread(name=thread_name[:THREAD_NAME_MAX_LEN])
    await thread.send(f"<@&{settings.notify_role_id}>\nreactions:")
    return True


async def reaction_change_handler(payload):
    if payload.user_id == client.user.id:
        return
    try:
        channel = await resolve_channel(payload.channel_id)
        if channel is None:
            return
        message = await channel.fetch_message(payload.message_id)
        if message.position is None and message.flags.has_thread:
            await update_reaction_msg(message)
    except Exception:
        logging.error(traceback.format_exc())


def get_thread_name(message_content):
    title = re.search(r"\[[^\]]*\]", message_content)
    return title.group(0) if title is not None else None


def reactions_to_str(reactions):
    message = "reactions:\n"
    for reaction in reactions:
        message += str(reaction.emoji) + ":" + str(reaction.count) + "    "
    return message


async def get_thread_for_message(message):
    thread = None
    if message.guild is not None:
        thread = message.guild.get_thread(message.id)
    if thread is None:
        thread = discord.utils.get(getattr(message.channel, "threads", []), id=message.id)
    if thread is not None:
        return thread
    try:
        fetched = await client.fetch_channel(message.id)
    except (discord.NotFound, discord.Forbidden, discord.HTTPException):
        return None
    if isinstance(fetched, discord.Thread):
        return fetched
    return None


async def get_reaction_msg(message):
    thread = await get_thread_for_message(message)
    if thread is None:
        return None
    if thread.archived:
        try:
            await thread.edit(archived=False)
        except discord.HTTPException:
            logging.error("Could not unarchive thread %s", thread.id)
            return None
    messages = [msg async for msg in thread.history(limit=2, oldest_first=True)]
    if len(messages) < 2 or messages[1].author != client.user:
        return None
    return messages[1]


async def update_reaction_msg(message):
    reaction_msg = await get_reaction_msg(message)
    if reaction_msg is not None:
        reaction_msg_content = reactions_to_str(message.reactions)
        await reaction_msg.edit(content=(f"<@&{settings.notify_role_id}>\n" + reaction_msg_content))


@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))


@client.event
async def on_message(message):
    await new_message_handler(message)


@client.event
async def on_raw_reaction_add(payload):
    await reaction_change_handler(payload)


@client.event
async def on_raw_reaction_remove(payload):
    await reaction_change_handler(payload)


client.run(settings.client_token)
