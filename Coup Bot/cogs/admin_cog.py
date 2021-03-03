'''
File: admin_cog.py
Author: Gavin Vogt
This program defines the Admin cog for the Coup Bot
'''

# dependencies
from discord.ext import commands

# my code
from cogs.base_cog import BaseCog


# Define help strings
LOAD_HELP = "Loads a cog"
RELOAD_HELP = "Reloads a cog"
QUIT_HELP = "Shuts down the bot"


class AdminCog(BaseCog, name="admin"):
    '''
    Owner-only admin commands for the Coup Bot
    '''
    def __init__(self, bot):
        super().__init__(bot)

    async def cog_check(self, ctx):
        '''
        Commands in this cog can only be called by the bot owner
        '''
        return await self.bot.is_owner(ctx.author)

    @commands.command(name="debug", help="Print out the debug game summary")
    @commands.guild_only()
    async def debug_current_game(self, ctx):
        game = self.bot.get_game(ctx.channel.id)
        if game is None:
            print(f"No game in channel {ctx.channel}")
        else:
            print()
            game.print_summary()

    @commands.command(name="load", help=LOAD_HELP)
    async def load_extension(self, ctx, extension_name):
        '''
        Allows bot owner to reload an extension by name,
        from a file of the form {cog_name}_cog.py
        '''
        # Load the extension
        self.bot.load_extension('cogs.' + extension_name + '_cog')
        await ctx.send(f"Extension `{extension_name}` loaded")

    @commands.command(name="reload", help=RELOAD_HELP)
    async def reload_extension(self, ctx, extension_name):
        '''
        Allows bot owner to reload an extension by name,
        from a file of the form {cog_name}_cog.py
        '''
        # Reload the extension
        self.bot.reload_extension('cogs.' + extension_name + '_cog')
        await ctx.send(f"Extension `{extension_name}` reloaded")

    @commands.command(name="quit", help=QUIT_HELP)
    async def quit(self, ctx):
        '''
        Shuts down the bot
        '''
        print(f"Shut down by {ctx.author} (id={ctx.author.id})")
        await ctx.send("Shutting down")
        await self.bot.close()
        input("Press enter to close ")


def setup(bot):
    bot.add_cog(AdminCog(bot))