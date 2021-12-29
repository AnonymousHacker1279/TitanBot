import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from Framework.Commands.UserConfig import UserConfig
from Framework.ModuleSystem.Modules import ModuleSystem
from Framework.Commands.Quotes import Quotes
from Framework.Commands.RevokeCommandAccess import RevokeCommandAccess
from Framework.Commands.HelpCommand import Help


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='$', intents=intents)

bot.help_command = Help()

bot.add_cog(ModuleSystem())
bot.add_cog(UserConfig())
bot.add_cog(Quotes())
bot.add_cog(RevokeCommandAccess())


@bot.event
async def on_ready():
	print('Connected to Discord!')
	await bot.change_presence(activity=discord.Game('Inflicting pain on humans'))


bot.run(TOKEN)
