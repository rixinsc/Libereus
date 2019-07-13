from discord.ext import commands
from core.helper import log, sendError
from core.scripts import decode
from core.classes import ExtensionBase
from core.exceptions import CommandErrorHandled
import time
import asyncio
import discord # for eval use, don't remove
import json

class Owner(ExtensionBase):
	"""Owner commands."""
	async def cog_check(self, ctx):
		if not await ctx.bot.is_owner(ctx.author):
			raise commands.errors.NotOwner('You do not own this bot.')
		return True

	@commands.command()
	async def eval(self, ctx):
		"""Evaluate something."""
		content = ctx.message.content[len(ctx.prefix)+len(ctx.invoked_with)+1:]
		if content == "" or content == None or content == " ":
			await ctx.send('Cannot evaluate an empty string.')
			return
		try:
			result = eval(content)
			await ctx.send(f'```py\n{result}\n```')
		except Exception as e:
			await sendError(ctx, e)
			raise CommandErrorHandled()

	@commands.command()
	async def shell(self, ctx, *, cmd: str):
		"""A system shell, does not support command persistance."""
		p = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
		msg = await ctx.send("Executing...")
		try:
			stdout, stderr = (None, None)
			tbefore = time.perf_counter()
			stdout, stderr = await asyncio.wait_for(p.communicate(), 360)
			tafter = time.perf_counter()
		except asyncio.TimeoutError:
			log(content=f'Command "shell" timed out.')
			await msg.edit(content="Process timed out.")
		except asyncio.CancelledError:
			log(content="Process cancelled.")
			await msg.edit(content="Process cancelled.")
			await p.terminate()
		if p.stderr == None:
			await msg.edit(content=f"```py\nExit code: {p.returncode}\n{decode(stdout)}\nTook {round((tafter-tbefore)*1000, 2)}ms```")
		else:
			await msg.edit(content=f"```py\nExit code: {p.returncode}\nStdout:\n{decode(stdout)}\nStderr:\n{decode(stderr)}\nTook {round((tafter-tbefore)*1000, 2)}ms```")

	@commands.command()
	async def shutdown(self, ctx):
		"""Shutdown the bot."""
		await ctx.send("Shutting down...")
		await asyncio.sleep(1)
		await self.bot.logout()

	@commands.command()
	async def prefix(self, ctx, *, pre):
		"""Change Prefix."""
		with open('settings.json', 'r', encoding='utf-8') as jfile:
			prefixes = json.load(jfile)
		prefixes[str(ctx.guild.id)] = pre
		await ctx.send(f'{pre} new prefix add')
		with open('settings.json', 'w', encoding='utf-8') as jfile:
			json.dump(prefixes, jfile, indent=4)


def setup(bot):
	bot.add_cog(Owner(bot))