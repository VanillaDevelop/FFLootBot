from Bot.DiscordBot import DiscordBot
from dotenv import load_dotenv
import os

load_dotenv()

DEBUG_SERVERS = [283246352182411265]

bot = DiscordBot(debug_guilds=DEBUG_SERVERS)
bot.run(os.getenv('BOT_TOKEN'))
