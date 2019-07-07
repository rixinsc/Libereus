from discord.ext import commands
from core import exceptions
import traceback
import discord
import sys

__doc__ = "Bot's helper functions, contains various functions that the whole bot is using."

async def sendError(ctx, err, cdreset:bool=False, *, wrapped:bool=False, defaultcheck:bool=False) -> None:
	"""
	coroutine - Send Error
	Formats error message and send it.

	Usage: await sendError(context, error, cooldownreset=False, *, wrapped=False, defaultcheck=False)
	error = error object or string to send
	cooldownreset = Did it need to reset command cooldown?
	wrapped = If this is set to True, then it will not send the original exception and instead send a basic error message
	defaultcheck = Did it need to perform a default error checking before sending customized error?
	"""
	if isinstance(err, commands.CommandInvokeError):
		err = err.original
	standardErr = False # is the error a valid exception?

	if cdreset and not isinstance(err, commands.CommandOnCooldown):
		ctx.command.reset_cooldown(ctx)
	if defaultcheck and await decheck(ctx, err):
		return
	try:
		tberr = traceback.format_exception(type(err), err, err.__traceback__)
		tberr = ''.join(tberr)
		standardErr = True
	except AttributeError:
		tberr = err
	except:
		eprint("An error occured while parsing a command error. The error is shown below:\n{}".format(err))
		tberr = err
	log(ctx, 'err', content=tberr)
	if wrapped:
		await ctx.send("Uh-oh, seems like something unexpected happened. Please try again in a few minutes or contact the developer about this.")
	elif standardErr:
		await ctx.send('An error occured. The exception is shown below:\n```py\n{}: {}\n```'.format(type(err).__name__, err))
	else:
		await ctx.send('An error occured. The exception is shown below:\n```py\n{}\n```'.format(err))

async def cmderr(ctx, err, cdreset:bool=False, **kwargs) -> None:
	"""
	coroutine - Command Error
	Extended erroring message handler, specially designed for error in command.
	Use this when handling multiple exceptions.

	Usage: await cmderr(context, error, cooldownreset, [pderr = mode + 'message'])
	pderr: Predefined error, define a default message to send when this error occurs.
	The predefined error as string. Change '_' to '.', and '__' to '_'.
	Currently imported module: discord.ext.commands, discord
	cooldownreset = Did it need to reset command cooldown?

	mode: r | e
	r = send raw message
	e = send error message with default error syntax

	Raise
	AttributeError - if didn't specify a correct prefix.
	"""
	if isinstance(err, commands.CommandInvokeError):
		err = err.original
	try:
		tberr = traceback.format_exception(type(err), err, err.__traceback__)
		tberr = ''.join(tberr)
	except AttributeError:
		tberr = err
	except Exception as exp:
		eprint("An error occured while parsing a command error. The error is shown below:\n{}".format(
			''.join(traceback.format_exception(type(exp), exp, exp.__traceback__))
			))
		tberr = err

	if cdreset and not isinstance(err, commands.CommandOnCooldown):
		ctx.command.reset_cooldown(ctx)

	for pderr, msg in kwargs.items():
		pderr = pderr.replace('_', '.').replace('..', '_')
		if isinstance(err, eval(pderr)): #when error match
			if msg.startswith('e'):
				log(ctx, 'err', content=tberr)
				await sendError(ctx, msg[1:])
			elif msg.startswith('r'):
				log(ctx, 'err', content=tberr)
				await ctx.send(msg[1:])
			else:
				await sendError(ctx, msg)
				raise AttributeError(f'"{msg[0]}" is not a valid prefix.')
			return
	if await decheck(ctx, err):
		return
	await sendError(ctx, err)

async def decheck(ctx, err) -> bool:
	"""
	coroutine - Default Error Check
	If prespecified error occured, do something and return True.
	Else return False.

	Usage: await decheck(context, exception) -> bool
	"""
	# IMPORTANT: Return True if no further error handling is needed
	# IMPORTANT: Use 'tberr' if need traceback log, else use 'notberr'.
	if isinstance(err, commands.CommandInvokeError):
		err = err.original
	try:
		tberr = traceback.format_exception(type(err), err, err.__traceback__)
		tberr = ''.join(tberr)
	except AttributeError:
		tberr = err
	finally:
		notberr = '{}: {}'.format(type(err).__name__, err)
	if isinstance(err, commands.CommandNotFound):
		log(ctx, 'err', content=notberr)
		return True
	if isinstance(err, exceptions.CommandErrorHandled):
		log(ctx, 'err', content=notberr)
		return True
	if isinstance(err, commands.errors.CheckFailure): # when command check fail
		log(ctx, 'err', content=notberr, reason='failing command check') # No traceback
		await ctx.send('You do not have permission to execute this command.')
		return True
	if isinstance(err, commands.errors.MissingPermissions):
		log(ctx, 'err', content=notberr, reason="user missing permission")
		await ctx.send("You need `{}` permission to do so.".format(err.missing_perms))
		return True
	if isinstance(err, commands.errors.BotMissingPermissions):
		log(ctx, 'err', content=notberr, reason="bot missing permission")
		await ctx.send("I need `{}` permission to do this.".format(err.missing_perms))
		return True
	if isinstance(err, commands.CommandOnCooldown):
		log(ctx, 'err', content=tberr, reason=f'command is currently on cooldown type {err.cooldown.type}')
		await ctx.send(f"Command `{ctx.command}` is currently on cooldown. Please retry after {int(err.retry_after)} seconds.")
		return True
	if isinstance(err, (commands.errors.MissingRequiredArgument, commands.errors.BadArgument, commands.errors.TooManyArguments)): #using command improperly
		log(ctx, 'err', content=notberr, reason="command argument error")
		#send help
		if ctx.invoked_subcommand:
		    await ctx.send_help(str(ctx.invoked_subcommand))
		else:
		    await ctx.send_help(str(ctx.command))
		return True
	if isinstance(err, discord.Forbidden):
		log(ctx, 'err', content=tberr, reason='received 403 Forbidden')
		await ctx.send(f"Oops, I got an error while processing the request. Seems like I lack the permission to do that, can you correct it and try again?")
		return True
	if isinstance(err, discord.HTTPException):
		log(ctx, 'err', content=tberr, reason='an HTTP Exception occured')
		await sendError(ctx, err, wrapped=True)
		return True
	if isinstance(err, commands.errors.DisabledCommand):
		log(ctx, 'err', content=notberr, reason="command is disabled")
		await ctx.send(":x: This command is disabled.")
		return True
	if isinstance(err, commands.errors.UserInputError):
		log(ctx, 'err', content=tberr, reason='an error in user input')
		await sendError(ctx, err, wrapped=True)
		return True
	if isinstance(err, (discord.GatewayNotFound, discord.ConnectionClosed, discord.LoginFailure, discord.NoMoreItems)):
		stdeprint(ctx, err)
		return True
	if isinstance(err, (discord.opus.OpusError, discord.opus.OpusNotLoaded, discord.ClientException)):
		stdeprint(ctx, err)
		await sendError(ctx, err, wrapped=True)
		return True
	return False

def eprint(*objects, sep:str=' ', end:str='\n', flush:bool=False) -> None:
	"""
	Exception print
	Print to stderr, just a shorter way to do print(*objects, file=sys.stderr).

	Usage: eprint(value, ..., sep=' ', end='\\n', flush=False)
	"""
	new_objects = []
	for obj in objects:
		new_objects.append(tsl(obj))
	print(*new_objects, sep=sep, end=end, file=sys.stderr, flush=flush)

def sprint(*objects, **kwargs) -> None:
	"""
	Safe Print
	Just like print function, but it will escape non-bmp characters if console doesn't support it.

	Usage: sprint(value, ..., sep=' ', end='\\n', file=sys.stdout, flush=False)
	"""
	new_objects = []
	for obj in objects:
		new_objects.append(tsl(obj))
	print(*new_objects, **kwargs)

def stdeprint(context, exception) -> None:
	"""
	Standard Error Print
	Print an error using discord.py's default syntax (with full traceback).

	Usage: stdeprint(context, exception)
	"""
	print('Ignoring exception in command {}:'.format(context.command), file=sys.stderr)
	traceback.print_exception(type(exception), exception, exception.__traceback__, file=sys.stderr)

def log(ctx=None, type:str='debug', **kwargs) -> None:
	"""
	Log

	Usage: log(ctx, type='debug', [content, reason])
	·log(ctx, 'general')
	·log(ctx, 'error', reason='reason', content='content')
	·debug: log(content='content') (DEFAULT)
	"""
	type = type.lower()
	if not ctx:
		pass
	elif isinstance(ctx.channel, discord.TextChannel):
		guild_name = ctx.guild.name
		channel_name = "#" + ctx.channel.name
	elif isinstance(ctx.channel, discord.DMChannel):
		guild_name = "Personal DM"
		channel_name = ctx.channel.recipient
	elif isinstance(ctx.channel, discord.GroupChannel):
		guild_name = "Group DM"
		channel_name = str(ctx.channel)

	if type == "general" or type == "gen":
		sprint(f'{guild_name}({channel_name}), {ctx.author} > {ctx.message.content}\n')
	elif type == 'error' or type == "err":
		content = str(kwargs.get('content', ''))
		sprint(f'{guild_name}|{channel_name}|{ctx.author}: "{ctx.message.content}" -\n' + 
			'Error has been ignored{}: \n'
			.format(' because '+kwargs.get('reason','')), (
				content if content.endswith('\n') else content + '\n'
				))
	elif type == "debug" or type == "d":
		sprint("Debug: {}".format(kwargs.get('content','')))

try:
	non_bmp_map = None
	print("Console support non-bmp character. \U0001f389")
except UnicodeEncodeError:
	non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
	# Compat with python IDLE
	print("Console only support bmp character. All non-bmp character will be translated to the replacement character (U+FFFD).")

def tsl(text: str) -> str:
	"""
	Translate characters that python can't handle to codepoints.
	"""
	global non_bmp_map
	if non_bmp_map is not None:
		return str(text).translate(non_bmp_map)
	else:
		return str(text)