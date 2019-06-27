from discord.ext import commands
import discord

class ExtensionBase(commands.Cog):
	def __init__(self, bot, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.bot = bot

class Bot(commands.AutoShardedBot):
	async def on_message(self, ctx):
		if not self.is_ready() or \
		ctx.author.bot or \
		not (isinstance(ctx.channel, discord.DMChannel) or \
		ctx.channel.permissions_for(ctx.guild.me).send_messages):
			return
		await self.process_commands(ctx)