'''
File: base_cog.py
Author: Gavin Vogt
This program defines the BaseCog class, which inherits from commands.Cog
and will be used by other cogs to inherit default functionality
'''

# dependencies
from discord.ext import commands
import traceback


class BaseCog(commands.Cog):
    '''
    The BaseCog class will be used as a superclass by other cogs
    so they have access to the following default functionality:
        - cog_unload
        - cog_command_error
    '''
    def __init__(self, bot):
        '''
        Constructs the default Cog by storing a reference to the bot
        '''
        self.bot = bot

    def cog_unload(self):
        '''
        Displays default cog unload message
        '''
        print(f'Unloading cog `{self.qualified_name}`')

    async def cog_command_error(self, ctx, error):
        '''
        Handles errors by printing the error traceback
        '''
        print(f"ERROR in cog `{self.qualified_name}`:")
        traceback.print_exc()
        print("-----------" * 10 + "\n")
