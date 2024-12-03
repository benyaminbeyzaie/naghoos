import discord
from discord.ext import tasks
import datetime
from dotenv import load_dotenv
import os
import pytz

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

MESSAGES = {
    "16:30": {
        1313509328346546219: "Bip Bip, Looks like a great day today!"
    }
}

intents = discord.Intents.default()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    schedule_messages.start()

@tasks.loop(seconds=60)
async def schedule_messages():
    cet = pytz.timezone('Europe/Paris')
    now = datetime.datetime.now(cet)
    current_time = now.strftime("%H:%M")
    
    if current_time in MESSAGES:
        for channel_id, message in MESSAGES[current_time].items():
            channel = client.get_channel(channel_id)
            if channel:
                await channel.send(message)

client.run(TOKEN)
