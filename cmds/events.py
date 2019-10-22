from discord.ext import commands
from core.helper import decheck, sendError, logger
from core.classes import ExtensionBase


class Events(ExtensionBase):
        """Handles bot events."""
        def __init__(self, bot, **options):
                super().__init__(bot, **options)
                self.extra_events = {}

        @commands.Cog.listener()
        async def on_command_error(self, ctx, e):
                #Check if command has custom error handler
                if self.extra_events.get('on_command_error', None):
                        return
                if hasattr(ctx.command, 'on_error'):
                        return
                cog = ctx.cog
                if cog:
                        attr = '_{0.__class__.__name__}__error'.format(cog)
                        if hasattr(cog, attr):
                                return

                if await decheck(ctx, e): #Check for default error
                        return
                #change to logging
                logger.info(content="No custom error handler found, using default handler.")
                await sendError(ctx, e)

        @commands.Cog.listener()
        async def on_command_completion(self, ctx):
            logger.info('{guild_name}({channel}), {author} > {command}'.format(guild_name=ctx.guild.name,
                                                                               channel=ctx.message.channel,
                                                                               author=ctx.message.author,
                                                                               command=ctx.message.content))

def setup(bot):
        bot.add_cog(Events(bot))
