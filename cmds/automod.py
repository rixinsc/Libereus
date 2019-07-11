from discord.ext import commands, tasks
from core.classes import ExtensionBase
from core.helper import log, cmderr, eprint
import discord
from random import randint
import datetime

class Automod(ExtensionBase):
	"""Auto moderation commands."""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.strikeReset.start()
		
	@commands.command()
	@commands.has_permissions(kick_members=True)
	async def prunemembers(self, ctx, days: int, include_no_message: bool = False):
		"""Prune inactive member (i.e. no message sent) given an inactive interval(days, minimum 1).
		Note that join/pin system message will also be considered as user's message.
		"""
		if days == 0 and include_no_message:
			await ctx.send("Pruning members with no message...")
		elif days < 1:
			await ctx.send("Interval too short, minimum accepted interval is 1.")
			return
		elif days >= 1100:
			await ctx.send("Interval too long, please consider lowering it.")
			return
		no_activity_members = []
		inactive_members = []
		last_msgs = []
		status_msg_content = "Searching and collecting data, this could take some time..."
		status_msg = await ctx.send(status_msg_content)
		guild_members = ctx.guild.members
		for pos, member in enumerate(guild_members):
			if member.bot: continue
			for channel in ctx.guild.text_channels:
				try:
					history = await channel.history().get(author__id=member.id)
					if history is not None: last_msgs.append(history)
				except discord.errors.Forbidden:
					pass
			while len(last_msgs) > 1:
				if last_msgs[0].created_at > last_msgs[1].created_at: # message is older
					last_msgs.append(last_msgs[0]) # append to the last
				del last_msgs[0]
			last_msg = last_msgs[0] if last_msgs else None
			# for those didn't send a message
			if last_msg == None and include_no_message:
				no_activity_members.append(member)
			elif last_msg == None:
				continue
			elif (datetime.datetime.now() - last_msg.created_at).days > days:
				inactive_members.append(member)
			last_msgs.clear()
			# Progress
			if pos % 2 == 0:
				 await status_msg.edit(content = status_msg_content + "\n{percentage}% ({current}/{total} processed)".
				 	format(percentage=round((pos+1)/len(guild_members)*100), current=pos+1, total=len(guild_members)))
		# status report
		await status_msg.edit(content = status_msg_content + "done")
		if no_activity_members:
			await ctx.send(
				"User that have no message in the server:\n{ulist}".
				format(ulist='\n'.join(['- '+str(m) for m in no_activity_members])))
		if inactive_members:
			await ctx.send(
				"User who haven’t sent any messages in the past {count} day{s}:\n{ulist}".
				format(count=days, s='s' if days>1 else '', 
					ulist='\n'.join(['- '+str(m) for m in inactive_members])))
		# Kicking
		rand = randint(1000, 9999)
		count = len(no_activity_members)+len(inactive_members)
		if count != 0:
			await ctx.send(
				"<@!{uid}> Are you sure you want to kick these {count} members?\nType `yes {rand}` or `(n)o` to cancel.".
				format(uid=ctx.author.id, count=len(no_activity_members)+len(inactive_members),rand=rand))
		else:
			await ctx.send("{mention} There're currently no inactive user, good job!".
				format(mention=ctx.author.mention))
			return
		try:
			response = await self.bot.wait_for('message', 
				check=lambda msg: msg.author == ctx.author and msg.channel == ctx.channel, 
				timeout=120.0)
		except TimeoutError:
			await ctx.send("Timeout reached, task cancelled.")
		response.content = response.content.lower()
		if response.content == f"yes {rand}":
			kick_status = await ctx.send("Kicking users...")
			for m in no_activity_members:
				log(content=f"Kicking {m} (no activity)")
				await ctx.guild.kick(m, 
					reason="Haven't send a single message in the server, requested by {member}.".
					format(member=ctx.author))
			for m in inactive_members:
				log(content=f'Kicking {m} (inactive)')
				await ctx.guild.kick(m, 
					reason="Haven't send a message in {days} days, requested by {member}.".
					format(days=days, member=ctx.author))
			await kick_status.edit(content="Kicked out {count} users.".
				format(count=len(no_activity_members)+len(inactive_members)))
		elif response.content in ('n', 'no'):
			await ctx.send("Task aborted.")
		elif response.content in ('c', 'cancel'):
			await ctx.send("Task cancelled.")
		else:
			await ctx.send("Invalid response, task cancelled.")
	@prunemembers.error
	async def errPrunemembers(self, ctx , err):
		await cmderr(ctx, err, 
			discord_Forbidden='r'+'I lack `Kick Members` permission.',
			discord_HTTPException='r'+'An error occured when kicking members. Please try again later.')
	
	@commands.command()
	@commands.has_permissions(manage_messages=True)
	async def wordfilter(self, ctx, status: bool = None):
		"""Toggle or change word filter's status."""
		if status is None:
			status = not self.bot.settings['moderation']['word filter']['enabled']
		new_settings = self.bot.settings
		new_settings['moderation']['word filter']['enabled'] = status
		self.bot.settings = new_settings
		await ctx.send("Changed word filter status to {status}.".format(status=status))
	@commands.Cog.listener('on_message')
	async def liveWordFilter(self, message):
		global strikes
		spaces = ('\u0020', '\u00a0', '\u1680', '\u2000', '\u2001', '\u2002', '\u2003', '\u2004', '\u2005', 
			'\u2006', '\u2007', '\u2008', '\u2009', '\u200a', '\u200b', '\u202f', '\u205f', '\u3000', '\u2800')
		symbols = ('.', '-', '_', '`', '~', ":", '/', '\\', ';', '+', '(', ')', '*', '^')
		regional_indicators = ('🇦','🇧','🇨','🇩','🇪','🇫','🇬','🇭','🇮','🇯','🇰','🇱','🇲','🇳','🇴','🇵','🇶','🇷','🇸','🇹','🇺','🇻','🇼','🇽','🇾','🇿')
		number_emojis = ('0⃣','1⃣','2⃣','3⃣','4⃣','5⃣','6⃣','7⃣','8⃣','9⃣')
		special_words = []
		settings = self.bot.settings['moderation']['word filter'].copy()

		if not settings['enabled']:
			return
		elif message.author == self.bot.user:
			return
		if settings['threshold'] < 1:
			eprint("Invalid threshold set({value}), value must be larger than 0.".
				format(value=settings['threshold']))
			return

		settings['words'] = list(set(settings['words'])) # Make element unique
		# Separate precise entries from words list
		for i, word in enumerate(settings['words']):
			word = word.lower()
			settings['words'][i] = word
			for space in spaces:
				if (space in word) and (word not in special_words):
					special_words.append(word)
					del settings['words'][i]
					break
			for symbol in symbols:
				if (symbol in word) and (word not in special_words):
					special_words.append(word)
					del settings['words'][i]
					break

		content = message.content.lower()
		# filter out possible seperator
		for c in spaces:
			content = content.replace(c, '')
		for s in symbols:
			content = content.replace(s, '')
		# convert regional indicator and number emojis to plain text
		for i,ri in enumerate(regional_indicators):
			content = content.replace(ri, chr(i+97))
		for i,ne in enumerate(number_emojis):
			content = content.replace(ne, chr(i+48))
		# detect bad word(s)
		if strikes.get(message.author, None) is None:
			strikes[message.author] = 0
		words = settings['words']
		striked = False
		for spword in special_words:
			if spword in message.content.lower():
				striked = True
				strikes[message.author] += 1
				break
		if not striked:
			for word in words:
				if word in content:
					striked = True
					strikes[message.author] += 1
					break
		if striked:
			await message.channel.send("🛑 {mention}, usage of bad word is not tolerated at here!".
				format(mention=message.author.mention))
		if strikes[message.author] >= settings['threshold']:
			if settings['action'].lower() == 'kick':
				await message.author.kick(reason="User exceeded word filter's limit | By Automod")
				strikes[message.author] = 0
			elif settings['action'].lower() == 'ban':
				await message.author.ban(reason="User exceeded word filter's limit | By Automod")
	@tasks.loop(hours=24)
	async def strikeReset(self):
		global strikes
		strikes = {}

def setup(bot):
	bot.add_cog(Automod(bot))
	global strikes
	strikes = {}
