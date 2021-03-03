'''
File: coup_bot.py
Author: Gavin Vogt
This program creates the Coup Bot for Discord
'''

# dependencies
from discord.ext import commands, tasks
from discord import Game
import traceback

# my code
from classes.coup_game import CoupGame
from helpers.command_checks import CustomCheckFailure


BOT_VERSION = '0.0.0'
initial_extensions = (
    'cogs.admin_cog',
    'cogs.setup_cog',
    'cogs.game_cog',
    'cogs.info_cog',
)

class CoupBot(commands.Bot):
    '''
    This class represents the Coup Discord Bot

    Useful methods:
        - get_game(channel_id)
        - set_game(channel_id, game)
        - remove_game(channel_id)
        - is_in_game(user_id)
        - set_user_status(user_id, in_game_status)
    '''

    VERSION = BOT_VERSION

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Keep track of games (max 1 per channel_id)
        self._games = {}

        # Keep track of users in games (only 1 game at a time per user)
        self._users = set()

        # Load all extensions
        for extension in initial_extensions:
            try:
                self.load_extension(extension)
            except Exception as e:
                print('Failed to load extension', extension)
                print('Error:', e)
                traceback.print_exc()

    async def on_command_error(self, ctx, exception):
        '''
        Overrides the on_command_error() method so when a CheckError
        occurs, the error message is sent to the user trying to call
        a command
        '''
        if isinstance(exception, CustomCheckFailure):
            await ctx.send(exception)
        else:
            await super().on_command_error(ctx, exception)

    async def on_connect(self):
        '''
        Start the update_status loop on connect
        '''
        self.update_status.start()

    async def on_disconnect(self):
        '''
        Stops the update_status loop on disconnect
        '''
        self.update_status.cancel()

    @tasks.loop(minutes=1)
    async def update_status(self):
        '''
        Updates the game status every minute to what the number of games is
        '''
        await self.change_presence(activity=Game(name=f"{self.game_count()} games"))

    def get_game(self, channel_id):
        '''
        Gets the Coup game occuring in the given channel
        channel_id: int, representing the ID of the channel
        Return: CoupGame object if there is a game in that channel, else None
        '''
        return self._games.get(channel_id)

    def set_game(self, channel_id, game):
        '''
        Sets up a Coup game for the given channel
        channel_id: int, representing the ID of the channel
        game: CoupGame being played in that channel
        '''
        self._games[channel_id] = game

    def game_count(self):
        '''
        Check the number of games being played
        '''
        return len(self._games)

    def remove_game(self, channel_id):
        '''
        Removes the Coup game for the given channel and automatically
        sets user statuses to not in game
        channel_id: int, representing the ID of the channel
        '''
        if channel_id in self._games:
            game = self._games[channel_id]
            for user_id in game.get_player_ids():
                # mark each user as no longer in a game
                self.set_user_status(user_id, False)
            del self._games[channel_id]

    def is_in_game(self, user_id):
        '''
        Checks if the given user is already in a game
        user_id: int, representing the user ID of the user to check
        '''
        return (user_id in self._users)

    async def process_player_remove(self, channel, game, player):
        '''
        Performs all the necessary actions for removing a player from the
        given game, and internally processes the player's removal. Used for
        `forfeit`, `kick`, `leave`, and if a player dies
        channel: Channel where player is being removed from game
        game: CoupGame player is being removed from
        player: Player being removed from the game
        '''
        user_id = player.get_id()
        if game.is_active():
            # player removed from an active game
            if game.remove_player(user_id):
                # it was that player's turn at the time
                await self.prompt_action(channel)
        else:
            # player left game with `leave` command
            game.unsign_up_player(user_id)

        # Clear user status
        self.set_user_status(user_id, False)
        if not game.is_over():
            # Transfer game master if game is still going on
            await self.transfer_master(channel, game, user_id)

    def set_user_status(self, user_id, in_game_status):
        '''
        Sets the status for a user
        user_id: int, representing the user ID of the user to set status for
        in_game_status: bool, representing whether the user is in a game
        '''
        if in_game_status:
            # user is now in a game
            self._users.add(user_id)
        else:
            # user is not in a game
            self._users.discard(user_id)

    async def transfer_master(self, channel, game, user_id):
        '''
        Transfers the master of the game to a random player in the
        game if the user_id belongs to the master, meaning
        that the master left the game
        '''
        if game.is_master(user_id):
            # Player leaving game was game master; transfer master
            new_master = game.random_player()
            game.set_master(new_master.id)
            await channel.send(f"Transferred game master to {new_master.mention}")

    async def prompt_action(self, channel):
        '''
        Prompts the correct player for their action
        channel: discord.Channel where game is being played
        '''
        game = self.get_game(channel.id)
        if game is not None and not game.is_over():
            # Ask the user for their action
            player = game.get_turn()
            await channel.send(f"Waiting for {player.get_mention()}'s action ...")