from discord.ext import commands
from core.classes import ExtensionBase
import discord

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
	async def slowmode(self, ctx, channels: commands.Greedy[discord.TextChannel] = None, seconds: int = 10):
		"""Set channel's slowmode delay, default to 10s."""
		if not (0 > seconds > (60*60*6)):
			await ctx.send(":x: The seconds are either too short or too long.")
		if channels is None: channel = [ctx.channel]
		for c in channels:
			channel.slowmode_delay = seconds
		await ctx.send("✅ Set {count} channel{s} with {sec}sec slowmode.".
			format(channel = len(channels), s='s' if len(channels)>1 else '', sec=seconds))

	@commands.command()
	@commands.has_permissions(manage_roles=True)
	async def mute(self, ctx, member: discord.Member, reason: str):
		"""Mute (denies `Send Messages` globally in a guild) a member in the guild with an optional reason.
		As of now, it needs a role named `Muted`."""
		mute_role = discord.utils.get(ctx.guild.roles, name='Muted')
		if mute_role == None:
			await ctx.send("The guild doesn't have `Mute` role !")
		else:
			await member.add_roles(mute_role, reason="Reason: {reason} | Requested by {mod}.".format(reason=reason, mod=ctx.author))
			embed = discord.Embed(color=0xfa144e)
			embed.add_field(name="Mute", value=f"{member} has been muted!")
			await ctx.send(embed=embed)

	@commands.command()
	@commands.has_permissions(manage_roles=True)
	async def unmute(self, ctx, member: discord.Member):
		"""Unmute previously muted user in the guild."""
		mute_role = discord.utils.get(ctx.guild.roles, name='Mute')
		await member.remove_roles(mute_role)
		embed = discord.Embed(color=0x91e873)
		embed.add_field(name="Mute", value=f"{member} has been un-muted!")
		await ctx.send(embed=embed)
		

def setup(bot):
	bot.add_cog(Moderation(bot))