import json
import discord
from discord.ext import commands
from datetime import datetime, timedelta
import asyncio
import requests
import time
from zones import zone_mapping

# Load configuration from config.json
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

# vars from config
api_url = config.get("api_url")
bot_token = config.get("bot_token")
command_prefix = config.get("commant_prefix")
bot_name = config.get("bot_name")
allowed_channels = config.get("allowed_channel_ids")
channel_message_id = config.get("channel_message_id")

# Discord Intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=command_prefix, intents=intents)
last_fetched_hour = None
current_terror_zone_memory = None
next_terror_zone_memory = None


allowed_channel_ids = config.get("allowed_channel_ids", [])
print("Allowed Channel IDs:", allowed_channel_ids)



def get_formatted_timestamp():
    return time.strftime("%Y-%m-%d %H:%M:%S")

@bot.event
async def on_ready():
    global user_notifications
    await bot.user.edit(username=bot_name)
    print("on_ready event triggered")
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    try:
        with open('subscriptions.json', 'r') as file:
            user_notifications = json.load(file)
        print("Loaded subscriptions:", user_notifications)
    except FileNotFoundError:
        with open('subscriptions.json', 'w') as file:
            file.write("{}")
        user_notifications = {}
        print("No subscription file found, initialized an empty dictionary.")
        
    if show_in_channel:
        current_terror_zone, next_terror_zone = get_terror_zones()
        updated_timestamp = get_formatted_timestamp()
        for channel_id in allowed_channel_ids:
            channel = bot.get_channel(channel_id)
            if channel:
                if channel_message_id:
                    try:
                        message = await channel.fetch_message(channel_message_id)
                        await message.edit(content=f"Current Terror Zone: {current_terror_zone}\nNext Terror Zone: {next_terror_zone} \nLast Updated: {updated_timestamp}")
                    except discord.NotFound:
                        message = await channel.send(f"Current Terror Zone: {current_terror_zone}\nNext Terror Zone: {next_terror_zone} \nLast Updated: {updated_timestamp}")
                        config["channel_message_id"] = message.id
                        with open('config.json', 'w') as config_file:
                            json.dump(config, config_file, indent=4)
                else:
                    message = await channel.send(f"Current Terror Zone: {current_terror_zone}\nNext Terror Zone: {next_terror_zone} \nLast Updated: {updated_timestamp}")
                    config["channel_message_id"] = message.id
                    with open('config.json', 'w') as config_file:
                        json.dump(config, config_file, indent=4)


    await notify_users()
    bot.loop.create_task(schedule_notifications())

# Show in Channel
show_in_channel = config.get("show_in_channel", False)
class CustomHelpCommand(commands.DefaultHelpCommand):
    async def send_bot_help(self, mapping):
        if self.context.channel.id in allowed_channels:
            await super().send_bot_help(mapping)
        else:
            await self.context.channel.send("The help command is not available in this channel.")
    async def command_callback(self, ctx, *, command=None):
        if ctx.channel.id not in allowed_channels and ctx.command.name == 'help':
            # Silently ignore the help command in disallowed channels
            return
        await super().command_callback(ctx, command=command)

bot.help_command = CustomHelpCommand()

try:
    with open('subscriptions.json', 'r') as file:
        user_notifications = json.load(file)
except FileNotFoundError:
    user_notifications = {}

# Get Terror Zone
def get_terror_zones():
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            current_zones = [zone_mapping[int(zone_id)] for zone_id in data['current']]
            next_zones = [zone_mapping[int(zone_id)] for zone_id in data['next']]
            current_terror_zone = ", ".join(current_zones)
            next_terror_zone = ", ".join(next_zones)
            return current_terror_zone, next_terror_zone
        else:
            print(f"Failed to fetch terror zone information. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {e}")
    return None, None

@bot.command(name='notify')
async def notify(ctx, *, zone: str):
    """Adds Specific zone to your notification list."""
    user_id = str(ctx.author.id)  # Convert user ID to string
    zone = zone.lower()
    try:
        with open('subscriptions.json', 'r') as file:
            user_notifications = json.load(file)
    except FileNotFoundError:
        user_notifications = {}

    if user_id not in user_notifications:
        user_notifications[user_id] = [zone]
        await ctx.send(f"You'll be notified for '{zone}'.")
    else:
        if zone not in user_notifications[user_id]:
            user_notifications[user_id].append(zone)
            await ctx.send(f"You'll be notified for '{zone}'.")

    save_subscriptions(user_notifications)

def save_subscriptions(subscriptions):
    try:
        with open('subscriptions.json', 'r') as file:
            existing_data = json.load(file)
            existing_data.update(subscriptions)
    except FileNotFoundError:
        existing_data = subscriptions

    with open('subscriptions.json', 'w') as file:
        json.dump(existing_data, file)

@bot.command(name='remove')
async def remove(ctx, *, zone: str):
    """Removes specific zone from your notification list."""    
    if ctx.channel.id not in allowed_channel_ids:
        return    
    user_id = str(ctx.author.id)  # Convert user ID to string
    zone_lower = zone.lower()

    try:
        with open('subscriptions.json', 'r') as file:
            user_notifications = json.load(file)
    except FileNotFoundError:
        user_notifications = {}

    if user_id in user_notifications:
        if zone_lower in [z.lower() for z in user_notifications[user_id]]:
            original_zone = next(z for z in user_notifications[user_id] if z.lower() == zone_lower)
            user_notifications[user_id].remove(original_zone)
            await ctx.send(f"You won't be notified for '{original_zone}' anymore.")
            save_subscriptions(user_notifications)
            return
    await ctx.send(f"You are not subscribed to '{zone}' notifications.")


async def notify_users():
    current_terror_zone, next_terror_zone = get_terror_zones()

    for user_id, zones in user_notifications.items():
        user = await bot.fetch_user(user_id)
        if user:
            matched_current = any(zone.lower() in current_terror_zone.lower() for zone in zones)
            matched_next = any(zone.lower() in next_terror_zone.lower() for zone in zones)
            try:
                if matched_current or matched_next:
                    message = ""
                    if matched_current:
                        message += f"New Terror Zone Detected: {current_terror_zone}\n"
                    if matched_next:
                        message += f"Upcoming Terror Zone: {next_terror_zone}\n"
                    await user.send(message.strip())
            except Exception as e:
                print(f"Failed to send message to user {user_id}: {e}")


@bot.command(name='notifications')
async def show_notifications(ctx):
    """Shows a list of zones you are subscribed to."""
    user_id = str(ctx.author.id)  # Convert user ID to string
    try:
        with open('subscriptions.json', 'r') as file:
            user_notifications = json.load(file)
    except FileNotFoundError:
        user_notifications = {}
    if user_id in user_notifications:
        user_zones = user_notifications[user_id]
        if user_zones:
            zones_list = "\n".join(user_zones)
            await ctx.send(f"Your current subscribed zones:\n{zones_list}")
        else:
            await ctx.send("You are not subscribed to any zones.")
    else:
        await ctx.send("You are not subscribed to any zones.")

@bot.command(name='current')
async def lookup(ctx):
    """Retrieves current and next terror zones.  Credits: d2emu.com"""
    print("Command executed in channel:", ctx.channel.id)
    print("Allowed Channel IDs:", allowed_channel_ids)
    
    if ctx.channel.id not in allowed_channel_ids:
        return
    global current_terror_zone_memory, next_terror_zone_memory
    current_terror_zone = current_terror_zone_memory
    next_terror_zone = next_terror_zone_memory
    if not current_terror_zone or not next_terror_zone:
        current_terror_zone, next_terror_zone = get_terror_zones()
    # Calculate time until next hour
    current_time = datetime.now()
    minutes_until_next_hour = 60 - current_time.minute if current_time.minute != 0 else 0
    # Format time remaining
    time_until_next_hour = f"{minutes_until_next_hour} minute{'s' if minutes_until_next_hour != 1 else ''}"
    # Send the retrieved terror zone information to the Discord channel along with time until next hour
    message = await ctx.send(f"Current Terror Zone: {current_terror_zone}\nNext Terror Zone: {next_terror_zone}\nTime until next zone change: {time_until_next_hour}")
    
    # Wait for 5 seconds
    await asyncio.sleep(5)
    
    # Delete the bot's message
    await message.delete()
    
    # Delete the user's message
    await ctx.message.delete()


async def schedule_notifications():
    while True:
        current_time = datetime.now()
        next_hour = (current_time.replace(second=0, microsecond=0, minute=1) + timedelta(hours=1)).timestamp()
        delay = next_hour - current_time.timestamp()
        await asyncio.sleep(delay)
        await notify_users()

        updated_timestamp = get_formatted_timestamp()
        if show_in_channel:
            current_terror_zone, next_terror_zone = get_terror_zones()
            for channel_id in allowed_channel_ids:
                channel = bot.get_channel(channel_id)
                if channel:
                    if channel_message_id:
                        try:
                            message = await channel.fetch_message(channel_message_id)
                            await message.edit(content=f"Current Terror Zone: {current_terror_zone}\nNext Terror Zone: {next_terror_zone} \nLast Updated: {updated_timestamp}")
                        except discord.NotFound:
                            message = await channel.send(f"Current Terror Zone: {current_terror_zone}\nNext Terror Zone: {next_terror_zone} \nLast Updated: {updated_timestamp}")
                            config["channel_message_id"] = message.id
                            with open('config.json', 'w') as config_file:
                                json.dump(config, config_file, indent=4)
                    else:
                        message = await channel.send(f"Current Terror Zone: {current_terror_zone}\nNext Terror Zone: {next_terror_zone} \nLast Updated: {updated_timestamp}")
                        config["channel_message_id"] = message.id
                        with open('config.json', 'w') as config_file:
                            json.dump(config, config_file, indent=4)


bot.run(bot_token)