from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
VERSION = os.getenv('BOT_VERSION')
UPDATE_LOCATION = os.getenv('BOT_UPDATE_LOCATION')
