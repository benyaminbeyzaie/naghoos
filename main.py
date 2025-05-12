import discord
from discord.ext import tasks
import datetime
from dotenv import load_dotenv
import os
import pytz
from openai import OpenAI

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

MESSAGES = {
    "11:00": {
        1280064375637409804: {
            "user_mentions": ["708219897108365332", "744614358717300738", "288473580679987201", "819884346126237696"],
            "exception_days": [WEEKDAYS[0], WEEKDAYS[3], WEEKDAYS[5], WEEKDAYS[6]]
        }
    },
}

intents = discord.Intents.default()
client = discord.Client(intents=intents)
open_ai_client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)

async def get_random_message():
    import random

    themes = ["pirate", "cowboy", "sci-fi", "Shakespeare", "hacker-slang", "robot", "80s action movie"]
    random_theme = random.choice(themes)
    try:
        response = open_ai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a fun and creative reminder bot."},
                {"role": "user", "content": f"Write a one-sentence reminder to a team of software engineers to submit their daily updates. Make it funny, creative, and based on a {random_theme} theme."}
            ],
            max_tokens=100,
            temperature=1.0
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating message: {e}")
        return "Bip Bip, This is a reminder!"

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
        for channel_id, config in MESSAGES[current_time].items():
            if now.strftime("%A") in config["exception_days"]:
                continue
            channel = client.get_channel(channel_id)
            if channel:
                random_message = await get_random_message()
                
                if isinstance(config, dict) and "user_mentions" in config:
                    mentions = " ".join([f"<@{user_id}>" for user_id in config["user_mentions"]])
                    random_message = f"{mentions} \n\n {random_message}"

                await channel.send(random_message)

client.run(TOKEN)
