#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
from discord.ext import commands
from core.helper import cmderr, sprint
from core.classes import Bot
import sys, os
import asyncio
import json
from discord import DMChannel
from pathlib import Path
from fnmatch import filter

if __name__ == "__main__":
	# Initialise
	if sys.platform == 'win32':
		loop = asyncio.ProactorEventLoop()
	else:
		loop = asyncio.get_event_loop()
	os.chdir(Path(__file__).resolve().parent)

	def get_prefix(bot, ctx):
		if not ctx.guild:
			return commands.when_mentioned_or('/', 'libereuse')(bot, ctx)
		with open('settings.json') as jfile:
			prefixes = json.load(jfile)
		if str(ctx.guild.id) not in prefixes:
			return commands.when_mentioned_or('/', 'libereuse')(bot, ctx)
		prefix = prefixes[str(ctx.guild.id)]
		return commands.when_mentioned_or(prefix)(bot, ctx)

	bot = Bot(command_prefix=get_prefix, pm_help=None, loop=loop)

	ext_path = "cmds"

	@bot.event
	async def on_ready():
		sprint('Logged in as {}\n'.format(bot.user))

	@bot.check
	async def useable(ctx):
		try:
			blacklist = ctx.bot.settings['blacklist']
			if not bot.is_ready() or ctx.author.bot:
				return False
			elif isinstance(ctx.channel, DMChannel):
				return False
			elif ctx.author.id == bot.owner_id:
				return True
			elif not ctx.channel.permissions_for(ctx.guild.me).send_messages:
				return False
			elif (ctx.author.id in blacklist['userID']) or (ctx.channel.id in blacklist['channelID']) or (ctx.guild.id in blacklist['guildID']):
				return False
			return True
		except Exception as e:
			raise RuntimeError from e

	@bot.command()
	@commands.is_owner()
	async def reload(ctx, component: str):
		"""Reload a component."""
		if component == 'settings':
			with open("settings.json", "r", encoding="utf8") as file:
				ctx.bot.settings = json.load(file, encoding='utf8')
			await ctx.send('Reloaded settings.')
			return
		await wildcardCheck(ctx, "reload", component)
	@bot.command()
	@commands.is_owner()
	async def unload(ctx, component: str):
		"""Unload a component."""
		await wildcardCheck(ctx, "unload", component)
	@bot.command()
	@commands.is_owner()
	async def load(ctx, component: str):
		"""Load a component."""
		await wildcardCheck(ctx, "load", component)

	async def wildcardCheck(ctx, method: str, query: str) -> None:
		if not method in ('load', 'unload', 'reload'):
			raise ValueError("Unsupported method {}.".format(method))
		msg = await ctx.send("{}ing component...".format(method.capitalize()))
		files = os.listdir(ext_path)
		files = [file[:-3] for file in os.listdir(ext_path) if file.endswith(".py")]
		components = filter(files, query)
		if method == 'reload':
			for comp in components:
				bot.reload_extension(f"{ext_path}.{comp}")
		elif method == 'unload':
			for comp in components:
				bot.unload_extension(f"{ext_path}.{comp}")
		elif method == 'load':
			for comp in components:
				bot.load_extension(f"{ext_path}.{comp}")
		components = ["`"+x+"`" for x in components]
		if not len(components) == 0:
			await msg.edit(content=f"{method.capitalize()}ed {', '.join(components)} component.")
		else:
			await msg.edit(content="No component matches your query.")

	@reload.error
	@unload.error
	@load.error
	async def errReload(ctx, e):
		await cmderr(ctx, e, 
			commands_errors_NotOwner='r'+'Only owner can use this command.', 
			commands_errors_MissingRequiredArgument="r"+f'Please specify a component to {ctx.command.name}.',
			commands_errors_ExtensionNotLoaded="r"+f"Can't {ctx.command.name}.  Extension hasn't been loaded.",
			commands_errors_NoEntryPointError="r"+"Extension doesn't have an entry point. (Missing `setup` function)",
			commands_errors_ExtensionNotFound="r"+"Extension not found.")

	for file in os.listdir(ext_path):
		if file.endswith(".py"):
			name = file[:-3]
			bot.load_extension(f"{ext_path}.{name}")

	bot.run(bot.settings['token'])
