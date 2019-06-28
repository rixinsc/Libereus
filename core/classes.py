from discord.ext import commands
import discord

class ExtensionBase(commands.Cog):
	def __init__(self, bot, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.bot = bot

class Bot(commands.AutoShardedBot):
	pass