from discord.ext import commands
import discord
import json

class ExtensionBase(commands.Cog):
	def __init__(self, bot, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.bot = bot

class Bot(commands.AutoShardedBot):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		with open("settings.json", "r", encoding="utf8") as file:
			self._settings = json.load(file, encoding='utf8')

	@property
	def settings(self):
		return self._settings
	@settings.setter
	def settings(self, obj):
		self._settings = obj
		with open("settings.json", "w", encoding="utf8") as file:
			file.seek(0, 0)
			json.dump(obj, file, indent=4)