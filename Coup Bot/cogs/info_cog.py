'''
File: info_cog.py
Author: Gavin Vogt
This program defines the Info cog for the Coup bot
'''

# dependencies
from discord.ext import commands
from discord import User

# my code
from cogs.base_cog import BaseCog
from helpers.command_checks import channel_has_game, is_player, game_is_started

# Define help strings
SETTINGS_HELP = "Show game settings"
COINS_HELP = "Checks how many coins you or another player have"
HAND_HELP = "Shows information about your or another player's hand"
DEAD_HELP = "Shows pile of dead cards"
SUMMARY_HELP = "Shows game summary"
COUNT_HELP = "Shows player count"
DN_HELP = "Find out for yourself"


class InfoCog(BaseCog, name="info"):
    '''
    Commands for getting various information about the current game
    '''
    def __init__(self, bot):
        super().__init__(bot)

    @commands.command(name="settings", help=SETTINGS_HELP)
    @channel_has_game()
    @commands.guild_only()
    async def send_game_settings(self, ctx):
        '''
        Sends the embed representing the game settings
        '''
        game = self.bot.get_game(ctx.channel.id)
        await ctx.send(embed=game.setup_embed(ctx.channel.mention))

    @commands.command(name="coins", help=COINS_HELP)
    @game_is_started()
    @is_player()
    @channel_has_game()
    @commands.guild_only()
    async def send_coin_count(self, ctx, user: User = None):
        '''
        Shows the player their coin count in the current game
        user: discord.User to show coin count of (optional)
        '''
        game = self.bot.get_game(ctx.channel.id)
        if user is None:
            player = game.get_player(ctx.author.id)
            await ctx.send(f"You have `{player.get_coins()}` coins")
        else:
            player = game.get_player(user.id)
            if player is None:
                await ctx.send(f"{user.mention} is not part of this game")
            else:
                await ctx.send(f"{user.mention} has `{player.get_coins()}` coins")

    @commands.command(name="hand", help=HAND_HELP)
    @game_is_started()
    @is_player()
    @channel_has_game()
    @commands.guild_only()
    async def show_hand(self, ctx, user: User = None):
        '''
        Shows the player their hand in the current game
        user: discord.User to show hand of (optional and only shows revealed cards)
        '''
        # Get the Player profile and send them their hand
        game = self.bot.get_game(ctx.channel.id)

        if user is None:
            player = game.get_player(ctx.author.id)
            await ctx.author.send(embed=player.get_embed(ctx))
        else:
            player = game.get_player(user.id)
            if player is None:
                await ctx.send(f"{user.mention} is not part of this game")
            else:
                await ctx.send(embed=player.get_visible_embed())

    @commands.command(name="dead", help=DEAD_HELP)
    @game_is_started()
    @channel_has_game()
    @commands.guild_only()
    async def show_dead_pile(self, ctx):
        '''
        Shows the pile of dead cards
        '''
        game = self.bot.get_game(ctx.channel.id)
        await ctx.send(embed=game.dead_embed())

    @commands.command(name="summary", help=SUMMARY_HELP)
    @game_is_started()
    @channel_has_game()
    @commands.guild_only()
    async def send_game_summary(self, ctx):
        '''
        Sends the game summary
        '''
        game = self.bot.get_game(ctx.channel.id)
        await ctx.send(embed=game.summary_embed())

    @commands.command(name="count", help=COUNT_HELP)
    @channel_has_game()
    @commands.guild_only()
    async def send_player_count(self, ctx):
        '''
        Sends the player count for the game in this channel
        '''
        game = self.bot.get_game(ctx.channel.id)
        await ctx.send(f"Current player count: `{game.player_count()}`")

    @commands.command(name="dn", help=DN_HELP, hidden=True)
    async def deez_nuts(self, ctx, user: User):
        if ctx.author.id == user.id:
            # tried to use command on self
            await ctx.send("You can't use this command on yourself")
        elif await self.bot.is_owner(user):
            # tried to use command on owner
            await ctx.send(f"Nice try; {user.mention} makes {ctx.author.mention} gargle deez nuts in retribution")
        else:
            await ctx.send(f"{user.mention} gargles deez nuts")


def setup(bot):
    bot.add_cog(InfoCog(bot))
