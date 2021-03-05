'''
File: launcher.py
Author: Gavin Vogt
This program launches the Coup Bot
'''

# dependencies
import discord
import os
from dotenv import load_dotenv
import logging

# my code
from coup_bot import CoupBot


# Set up logging
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord_bot_log.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


# Get the bot token
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")


# Set up the bot
BOT_DESCRIPTION = f'''Discord Coup Bot {CoupBot.VERSION}
Developed by Gavin Vogt
'''
PREFIX = "c!"
bot = CoupBot(
    command_prefix = PREFIX,
    #owner_id = YOUR_DISCORD_ID,
    description = BOT_DESCRIPTION,
)


############################## INITIATING BOT LOG ON #################################

@bot.event
async def on_ready():
    print(f"{bot.user} has successfully connected to Discord!")



if __name__ == "__main__":
    # Run the bot
    bot.run(TOKEN, reconnect=True)
