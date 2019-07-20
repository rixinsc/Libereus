import discord
from discord.ext import commands
from core.scripts import dcEscape
from core.classes import ExtensionBase
from random import randint
import time
import datetime

class Main(ExtensionBase):
	"""Core commands for bot."""
	@commands.command()
	async def ping(self, ctx):
		"""Delay between Discord and the websocket latency."""
		t = time.perf_counter()
		await ctx.trigger_typing()
		t2 = time.perf_counter()
		await ctx.trigger_typing()

		bot = round((t2 - t) * 1000)
		ws = int(self.bot.latency * 1000)
		await ctx.send(f'Pong!\nLatency: `{bot}ms` Websocket: `{ws}ms`')
			
	@commands.command()
	async def say(self, ctx, *, content: str):
		"""Say something."""
		msg = content.strip() #Remove whitespaces
		await ctx.send(dcEscape(msg, 'ping'))
		# TODO: Check perms before @everyone or @here

	@commands.command()
	async def calcdate(self, ctx, day: int):
		"""Add or subtract given day count by today and return."""
		td = datetime.datetime.now()
		today = datetime.date.today()
		tdelta = datetime.timedelta(days=day)
		result = today + tdelta
		dt = datetime.datetime.combine(result, td.time())
		embed = discord.Embed(timestamp=dt)
		await ctx.channel.send(embed=embed)

	@commands.command(aliases=['about'])
	async def info(self, ctx):
		embed = discord.Embed(title="About Libereus", description="Moderation made easy.")
		embed.set_thumbnail(url="https://sc.s-ul.eu/FEYj6UQg")
		embed.add_field(name="Developers", value=
			"Tansc#8171 (<@!399471491017605120>)\nProladon#7525 (<@!149772971555160064>)\nNRockhouse#4157 (<@!140526642916229120>)", 
			inline=True)
		embed.add_field(name="Version", value="0.1.3a build 1", inline=True)
		embed.add_field(name="Support Server", value="[Link](https://lihi1.cc/j2C5r)" , inline=True)
		embed.add_field(name="Powered by", value="discord.py v{}".format(discord.__version__), inline=True)
		embed.add_field(name="Source", value="[Link](https://github.com/Tansc161/Libereus)", inline=True)
		embed.add_field(name="License", value="Mozilla Public License 2.0", inline=True)
		embed.set_footer(text="Made with ❤")

		await ctx.send(embed=embed)

	@commands.command(aliases=["ms"])
	async def minesweeper(self, ctx, width: int = 10, height: int = 10, difficulty: int = 30):
		"""Tired of moderation? Here is a mini minesweeper game for you!
		(PS: Don't show spoiler content to experience the fun!)
		"""
		grid = tuple([['' for i in range(width)] for j in range(height)])
		num = ('0⃣','1⃣','2⃣','3⃣','4⃣','5⃣','6⃣','7⃣','8⃣')
		msg = ''

		if not (1 <= difficulty <= 100):
			await ctx.send("Please enter difficulty in terms of percentage (1-100).")
			return
		if width <= 0 or height <= 0:
			await ctx.send("Invalid width or height value.")
			return
		if width * height > 198:
			# 198 is the maximum number of emojis you can send in one Discord message. 
			# It is however undocumented by Discord, we found the number via our own research.
			return await ctx.channel.send("Your grid size is too big.")
			return
		if width * height <= 4:
			await ctx.send("Your grid size is too small.")
			return
		
		# set bombs in random location
		for y in range(0, height):
			for x in range(0, width):
				if randint(0, 100) <= difficulty:
					grid[y][x] = '💣'

		# now set the number emojis
		for y in range(0, height):
			for x in range(0, width):
				if grid[y][x] != '💣':
					grid[y][x] = num[sum((
						grid[y-1][x-1]=='💣' if y-1>=0 and x-1>=0 else False,
						grid[y-1][x]=='💣' if y-1>=0 else False,
						grid[y-1][x+1]=='💣' if y-1>=0 and x+1<width else False,
						grid[y][x-1]=='💣' if x-1>=0 else False,
						grid[y][x+1]=='💣' if x+1<width else False,
						grid[y+1][x-1]=='💣' if y+1<height and x-1>=0 else False,
						grid[y+1][x]=='💣' if y+1<height else False,
						grid[y+1][x+1]=='💣' if y+1<height and x+1<width else False
					))]
		await ctx.send(grid[y][x])

		# generate message
		for i in grid:
			for tile in i:
				msg += '||' + tile + '|| '
			msg += '\n'
		await ctx.send(msg)

	@commands.command()
	async def clean(self, ctx, nums: str):
		"""Purge bot message in channel with numbers or all."""
		bot_history = []
		try:
			if nums != 'all':
				async for message in ctx.channel.history(limit=500):
					if message.author == self.bot.user:
						bot_history.append(message)
				counte = 0
				for msg in bot_history[0:int(nums)]:
					counte += 1
					bot_msg = msg
					await bot_msg.delete()
				result = await ctx.channel.send('Deleted {} message(s).'.format(counte))
				await result.delete(delay= 3.0)
			elif nums == 'all':
				def is_bot(m):
					return m.author == self.bot.user				
				deleted = await ctx.channel.purge(limit=9999, check=is_bot)
				result = await ctx.channel.send('Deleted {} message(s).'.format(len(deleted)))
				await result.delete(delay= 3.0)
		except ValueError:
			await  ctx.send('Please enter the numbers or "all".')

def setup(bot):
	bot.add_cog(Main(bot))
