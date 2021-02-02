'''
File: setup_cog.py
Author: Gavin Vogt
This program creates the Setup cog for the Coup Bot. It provides
various commands for setting up a game of Coup
'''

# dependencies
from discord.ext import commands
from discord import User

# my code
from cogs.base_cog import BaseCog
from classes.coup_game import CoupGame
from helpers.command_checks import (channel_has_game, game_is_started,
                            game_not_started, is_player, is_game_master)

# General setup commands
JOIN_HELP = "Join the game in this channel"
LEAVE_HELP = "Leave the game in this channel"
PLAY_HELP = """Create a new game in this channel, making you the game master
Optional settings:
    - min_players | min         sets the minimum number of players in the game
    - max_players | max         sets the maximum number of players in the game
    - start_coins | coins       sets the number of starting coins per player
    - start_influences | cards  sets the number of starting influence cards
    - total_influences | total  sets the ideal total number of influence cards
      (NOTE: must be a multiple of 5, and if there are not enough cards
      for 2+ in the pile, the total will be increased)
"""

# Master only setup commands
MASTER_HELP = "Make another player the game master"
END_HELP = "Ends the game"
START_HELP = "Starts the game in this channel"


class SetupCog(BaseCog, name="setup"):
    '''
    Commands for setting up a game of Coup
    '''
    def __init__(self, bot):
        super().__init__(bot)


    ############################# GAME SETUP COMMANDS ###########################

    @commands.command(name="play", help=PLAY_HELP)
    @commands.guild_only()
    async def create_game(self, ctx, *, settings=None):
        '''
        Creates a new game in the channel
        settings: str, representing any settings for the game - allows
                  min_players, max_players, start_coins, and start_influences
        '''
        if self.bot.get_game(ctx.channel.id) is not None:
            await ctx.send("There is already an active game in this channel")
        elif self.bot.is_in_game(ctx.author.id):
            await ctx.send("You are already in a game in a different channel")
        else:
            # Create the game with any custom settings
            if settings is None:
                game = CoupGame(ctx.author.id)
            else:
                # User wants custom game settings
                game_settings = self._get_settings(settings)
                game = CoupGame(ctx.author.id,
                    min_players = game_settings.get("min_players"),
                    max_players = game_settings.get("max_players"),
                    start_coins = game_settings.get("start_coins"),
                    start_influences = game_settings.get("start_influences"),
                    card_count = game_settings.get("total_influences"),
                )

            # Store the game to the bot and join the author in automatically
            self.bot.set_game(ctx.channel.id, game)
            await self._attempt_join(ctx.channel, game, ctx.author)

            # Send game settings information
            setup_embed = game.setup_embed(ctx.channel.mention)
            setup_embed.description = f"Use `{self.bot.command_prefix}join` to join game"
            await ctx.send(embed=setup_embed)

    @commands.command(name="join", help=JOIN_HELP)
    @game_not_started()
    @channel_has_game()
    @commands.guild_only()
    async def join_game(self, ctx):
        '''
        Allows user to join the game
        '''
        # Try to add the player to the game
        game = self.bot.get_game(ctx.channel.id)
        await self._attempt_join(ctx.channel, game, ctx.author)

    @commands.command(name="leave", help=LEAVE_HELP)
    @is_player()
    @channel_has_game()
    @commands.guild_only()
    async def leave_game(self, ctx):
        '''
        Allows user to leave the game
        '''
        game = self.bot.get_game(ctx.channel.id)
        if game.is_active():
            # game already started - ask them to use forfeit command
            await ctx.send(f"Please use `{self.bot.command_prefix}forfeit` to forfeit the game")
        elif game.player_count() == 1:
            # Last player is leaving game; delete game
            self.bot.set_user_status(ctx.author.id, False)
            self.bot.remove_game(ctx.channel.id)
            await ctx.send("No players remain - game cancelled")
        else:
            game.unsign_up_player(ctx.author.id)
            self.bot.set_user_status(ctx.author.id, False)
            await ctx.send(ctx.author.mention + " left the game")
            await self.bot.transfer_master(game, ctx.author.id)


    ######################### GAME MASTER ONLY COMMANDS ##########################

    @commands.command(name="start", help=START_HELP)
    @is_game_master()
    @game_not_started()
    @channel_has_game()
    @commands.guild_only()
    async def start_game(self, ctx, start_player: User = None):
        '''
        Allows game master to start the game (must not have started yet)
        '''
        game = self.bot.get_game(ctx.channel.id)
        if not game.is_valid():
            await ctx.send(f"Player count must be between {game.get_min()} and {game.get_max()}")
        elif start_player is not None and not game.is_signed_up(start_player.id):
            await ctx.send(f"{start_player.mention} is not part of this game")
        else:
            # Start the game
            game.initialize_game()
            if start_player is None:
                # Randomize who starts the game
                game.randomize_turn()
            else:
                # Set the first player to be start_player
                game.set_turn_to(start_player.id)

            # Send the game summary and hands for reference
            await ctx.send(embed=game.summary_embed())
            for player in game.get_players():
                await player.get_user().send(embed=player.get_embed(ctx))

            # Prompt first user for their action
            await self.bot.prompt_action(ctx.channel)

    @commands.command(name="end", help=END_HELP, aliases=['cancel'])
    @is_game_master()
    @game_is_started()
    @channel_has_game()
    @commands.guild_only()
    async def end_game(self, ctx):
        '''
        Allows game master to end the game
        '''
        # Remove the game from the bot to cancel it
        game = self.bot.get_game(ctx.channel.id)
        bot.remove_game(ctx.channel.id)
        await ctx.send("Game cancelled")

    @commands.command(name="master", help=MASTER_HELP)
    @is_game_master()
    @channel_has_game()
    @commands.guild_only()
    async def transfer_master(self, ctx, new_master: User):
        '''
        Transfers game master to another user. They must already
        be part of the game
        '''
        game = self.bot.get_game(ctx.channel.id)
        if game.is_master(new_master.id):
            await ctx.send("You are already the game master")
        elif game.set_master(new_master.id):
            # Set new master successfully
            await ctx.send(f"{new_master.mention} is the new game master")
        else:
            # Other user is not part of the game
            await ctx.send(f"{new_master.mention} is not part of this game")


    ################################# HELPER METHODS ###############################

    def _get_settings(self, settings_str):
        '''
        Gets the settings specifed by the user
        settings_str: string to convert into a dict of settings
        '''
        settings_dict = {}
        settings = settings_str.split("--")
        for setting in settings:
            components = setting.split()
            if len(components) == 2:
                settings_dict[components[0]] = int(components[1])

        # Any properties that have multiple names
        if "min" in settings_dict:
            settings_dict["min_players"] = settings_dict["min"]
        if "max" in settings_dict:
            settings_dict["max_players"] = settings_dict["max"]
        if "coins" in settings_dict:
            settings_dict["start_coins"] = settings_dict["coins"]
        if "cards" in settings_dict:
            settings_dict["start_influences"] = settings_dict["cards"]
        if "total" in settings_dict:
            settings_dict["total_influences"] = settings_dict["total"]

        return settings_dict

    async def _attempt_join(self, channel, game, user):
        '''
        User attempting to join the given game
        channel: Channel to send join message to
        game: game to add player to
        user: User to add to the game
        '''
        if game.is_signed_up(user.id):
            # user is already signed up for the game
            await channel.send("You are already signed up for the game")
        elif self.bot.is_in_game(user.id):
            await channel.send("You are already in a game in a different channel")
        elif game.player_count() < game.get_max():
            # can join properly
            game.sign_up_player(user)
            self.bot.set_user_status(user.id, True)
            await channel.send(f"{user.mention} joined the game - player count {game.player_count()}")
        else:
            await channel.send(f"Maximum player count of `{game.get_max()}` exceeded; cannot join game")



def setup(bot):
    bot.add_cog(SetupCog(bot))
