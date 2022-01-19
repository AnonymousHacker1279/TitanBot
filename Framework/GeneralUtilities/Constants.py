import os

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
VERSION = os.getenv('BOT_VERSION')
UPDATE_LOCATION = os.getenv('BOT_UPDATE_LOCATION')
GENIUS_API_TOKEN = os.getenv('GENIUS_API_TOKEN')
