from Bot.DiscordBot import DiscordBot
from dotenv import load_dotenv
import os

load_dotenv()

bot = DiscordBot(load_config=True)
bot.run(os.getenv('BOT_TOKEN'))
