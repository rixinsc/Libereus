from discord.ext import commands
from core.classes import ExtensionBase
import discord
import json

class Moderation(ExtensionBase):
	"""Moderation commands."""

	@commands.command()
	@commands.has_permissions(manage_roles=True)
	async def lockdown(self, ctx, channels: commands.Greedy[discord.TextChannel] = None, reason: str = 'N/A'):
		"""Disable @everyone's permission to send message on given channel or current channel if not specified."""
		if channels is None:
			channels = [ctx.channel]
		for c in channels:
			await c.set_permissions(c.guild.default_role, send_messages=False, 
				reason="Reason: {reason} | Requested by {mod}.".format(reason=reason, mod=ctx.author))
			await c.send("🔒 Locked down this channel.")
		if not channels == [ctx.channel]:
			await ctx.send("Locked down {count} channel{s}.".format(count=len(channels), s='s' if len(channels)>1 else ''))
	@commands.command()
	@commands.has_permissions(manage_roles=True)
	async def unlock(self, ctx, channels: commands.Greedy[discord.TextChannel] = None, reason: str = 'N/A'):
		"""Reset @everyone's permission to send message on given channel or current channel if not specified."""
		if channels is None:
			channels = [ctx.channel]
		for c in channels:
			await c.set_permissions(c.guild.default_role, send_messages=None, 
				reason="Reason: {reason} | Requested by {mod}.".format(reason=reason, mod=ctx.author))
		await ctx.send("Unlocked {count} channel{s}.".format(count=len(channels), s='s' if len(channels)>1 else ''))

	@commands.command()
	@commands.has_permissions(manage_channels=True)
	async def slowmode(self, ctx, channels: commands.Greedy[discord.TextChannel] = None, seconds: int = 10, reason: str = "N/A"):
		"""Set channel's slowmode delay, default to 10s."""
		if not (0 <= seconds <= 21600):
			await ctx.send(":x: The seconds are either too short or too long.")
			return
		if channels is None: channels = (ctx.channel,)
		for c in channels:
			await c.edit(reason="Reason: {reason} | Requested by {mod}.".format(reason=reason, mod=ctx.author), slowmode_delay=seconds)
		if seconds != 0:
			await ctx.send("✅ Set {count} channel{s} with {sec}sec slowmode.".
				format(count = len(channels), s='s' if len(channels)>1 else '', sec=seconds))
		else:
			await ctx.send("✅ Disabled slowmode for {count} channel{s}.".
				format(count = len(channels), s='s' if len(channels)>1 else ''))

	@commands.command()
	@commands.has_permissions(manage_roles=True)
	async def mute(self, ctx, member: discord.Member, reason: str):
		"""Mute (denies `Send Messages` globally in a guild) a member in the guild with an optional reason.
		As of now, it needs a role named `Muted`."""
		mute_role = discord.utils.get(ctx.guild.roles, name='Muted')
		if mute_role == None:
			await ctx.send("The guild doesn't have `Mute` role ! Do u wanna create ones? (y/n)")
			try:
				response = await self.bot.wait_for('message', 
					check=lambda msg: msg.author == ctx.author and msg.channel == ctx.channel, 
					timeout=120.0)
			except TimeoutError:
				await ctx.send("Timeout reached, task cancelled.")
			response.content = response.content.lower()
			if response.content in ('y', 'yes'):
				perms = discord.Permissions()
				perms.update(send_messages=False, read_messages=True, speak=False, send_tts_messages=False)
				mute_role = await ctx.guild.create_role(name='Muted', Permission= perms)
				await ctx.send('Role created!')
				await member.add_roles(mute_role, reason="Reason: {reason} | Requested by {mod}.".format(reason=reason, mod=ctx.author))
				embed = discord.Embed(color=0xfa144e)
				embed.add_field(name="Mute", value=f"{member} has been muted!")
				await ctx.send(embed=embed)
			elif response.content in ('n', 'no'):
				await ctx.send("Task aborted.")
			elif response.content in ('c', 'cancel'):
				await ctx.send("Task cancelled.")
			else:
				await ctx.send("Invalid response, task cancelled.")
		else:
			await member.add_roles(mute_role, reason="Reason: {reason} | Requested by {mod}.".format(reason=reason, mod=ctx.author))
			embed = discord.Embed(color=0xfa144e)
			embed.add_field(name="Mute", value=f"{member} has been muted!")
			await ctx.send(embed=embed)

	@commands.command()
	@commands.has_permissions(manage_roles=True)
	async def unmute(self, ctx, member: discord.Member):
		"""Unmute previously muted user in the guild."""
		mute_role = discord.utils.get(ctx.guild.roles, name='Muted')
		await member.remove_roles(mute_role)
		embed = discord.Embed(color=0x91e873)
		embed.add_field(name="Mute", value=f"{member} has been un-muted!")
		await ctx.send(embed=embed)

	@commands.command(aliases=['unhoist'])
	@commands.has_permissions(manage_nicknames=True)
	async def dehoist(self, ctx):
		"""Remove hoisting character for members that attempt to hoist themselves."""
		hoist_chars = tuple(ctx.bot.settings['moderation']['hoisting characters'])
		members = ctx.guild.members
		status_msg = await ctx.send("Processing...")
		count = 0
		for m in members:
			if m.display_name.startswith(hoist_chars):
				await m.edit(nick=f"{m.display_name}x".strip(''.join(hoist_chars))[:-1])
				count += 1
		await status_msg.edit(content="✅ Removed hoisting characters for {count} member{s}.".
			format(count=count, s='s' if count>1 else ''))

	@commands.command()
	@commands.has_permissions(manage_roles=True)
	async def trust(self, ctx, user: discord.Member):
		"""Add user to trustlist"""
		with open('settings.json', 'r', encoding='utf-8') as jfile:
			trust_members = json.load(jfile)
		if user.id not in trust_members['trustlist']:
			trust_members['trustlist'].append(user.id)
			with open('settings.json', 'w', encoding='utf-8') as jdata:
				json.dump(trust_members, jdata, indent=4)
			embed = discord.Embed(color=0x91e873)
			embed.add_field(name="Trust", value='{} has been add in trustlist'.format(user))
			await ctx.send(embed=embed)
		else:
			await ctx.send('⚠ {} has already in trustlist.'.format(user))

	@commands.command()
	@commands.has_permissions(manage_roles=True)
	async def untrust(self, ctx, user: discord.Member):
		"""Remove user from trustlist"""
		with open('settings.json', 'r', encoding='utf-8') as jfile:
			trust_members = json.load(jfile)
		if user.id in trust_members['trustlist']:
			trust_members['trustlist'].remove(user.id)
			with open('settings.json', 'w', encoding='utf-8') as jdata:
				json.dump(trust_members, jdata, indent=4)
			embed = discord.Embed(color=0xfa144e)
			embed.add_field(name="Un-Trust", value="{} has been remove from trustlist.".format(user))
			await ctx.send(embed=embed)
		else:
			await ctx.send("⚠ {} dosen't exist in trustlist.".format(user))

	@commands.command(aliases=['clear', 'prune'])
	@commands.has_permissions(manage_messages=True)
	async def purge(self, ctx, nums: int):
		"""Purge message with numbers."""
		deleted = await ctx.channel.purge(limit=int(nums)+1)
		result = await ctx.channel.send('Deleted {} message(s).'.format(len(deleted) - 1))
		await result.delete(delay= 3.0)

def setup(bot):
	bot.add_cog(Moderation(bot))