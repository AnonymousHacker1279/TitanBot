import discord
from discord.ext import commands

from Framework.CommandGroups.Fun import Fun
from Framework.CommandGroups.UserConfig import UserConfig
from Framework.CommandGroups.Utility import Utility
from Framework.GeneralUtilities import Constants
from Framework.ModuleSystem.Modules import ModuleSystem
from Framework.CommandGroups.Quotes import Quotes
from Framework.CommandGroups.RevokeAccess import RevokeAccess
from Framework.CommandGroups.Help import Help


intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='$', intents=intents)

bot.help_command = Help()

bot.add_cog(ModuleSystem())
bot.add_cog(UserConfig())
bot.add_cog(Quotes())
bot.add_cog(Fun())
bot.add_cog(Utility())
bot.add_cog(RevokeAccess())


@bot.event
async def on_ready():
	print('Connected to Discord!')
	await bot.change_presence(activity=discord.Game('Inflicting pain on humans'))


bot.run(Constants.TOKEN)
