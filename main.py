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

# Maximum number of messages to fetch for summarization
MAX_MESSAGES_TO_SUMMARIZE = 100

intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent
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

async def summarize_channel_messages(messages):
    if not messages:
        return "No messages to summarize."
    
    # Format messages for OpenAI
    formatted_messages = []
    for msg in messages:
        if not msg.author.bot and msg.content:  # Skip bot messages and empty messages
            timestamp = msg.created_at.strftime("%H:%M")
            formatted_messages.append(f"{timestamp} - {msg.author.display_name}: {msg.content}")
    
    if not formatted_messages:
        return "No user messages found to summarize."
    
    messages_text = "\n".join(formatted_messages)
    
    try:
        response = open_ai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes Discord conversations."},
                {"role": "user", "content": f"Summarize the following Discord conversation in a concise way highlighting the main topics and key points discussed:\n\n{messages_text}"}
            ],
            max_tokens=300,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating summary: {e}")
        return "Sorry, I encountered an error while generating the summary."

@client.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == client.user:
        return
    
    # Check if the bot is mentioned and "summarize" is in the message
    if client.user.mentioned_in(message) and "summarize" in message.content.lower():
        channel = message.channel
        await message.channel.send("Generating summary, please wait...")
        
        # Fetch messages from the channel
        messages = []
        async for msg in channel.history(limit=MAX_MESSAGES_TO_SUMMARIZE):
            # Only include messages from today
            if msg.created_at.date() == datetime.datetime.now().date():
                messages.append(msg)
        
        # If there are channel mentions, use the first mentioned channel instead
        if message.channel_mentions:
            mentioned_channel = message.channel_mentions[0]
            await message.channel.send(f"Summarizing messages from {mentioned_channel.mention}...")
            
            messages = []
            async for msg in mentioned_channel.history(limit=MAX_MESSAGES_TO_SUMMARIZE):
                if msg.created_at.date() == datetime.datetime.now().date():
                    messages.append(msg)
        
        # Generate and send the summary
        summary = await summarize_channel_messages(messages)
        await message.channel.send(f"**Daily Summary**\n\n{summary}")

client.run(TOKEN)
