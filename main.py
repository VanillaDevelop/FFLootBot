from Bot.DiscordBot import DiscordBot
from dotenv import load_dotenv
import os

load_dotenv()

bot = DiscordBot(os.getenv('BOT_TOKEN'))