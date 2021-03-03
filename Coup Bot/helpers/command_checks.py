'''
File: command_checks.py
Author: Gavin Vogt
This program defines various command checks for the Coup Bot
'''

# dependencies
from discord.ext import commands

# my code
from classes.coup_game import CoupGame
from classes import actions

class CustomCheckFailure(commands.CheckFailure):
    '''
    Class that extends CheckFailure so the bot knows to send an
    error message in the channel for it
    '''
    pass

def channel_has_game():
    '''
    Checks that the channel has a game
    '''
    async def predicate(ctx):
        if ctx.bot.get_game(ctx.channel.id) is not None:
            # channel has a game
            return True
        else:
            raise CustomCheckFailure("No active game in this channel")
    return commands.check(predicate)

def game_is_started():
    '''
    Checks that the game has actually started
    '''
    async def predicate(ctx):
        game = ctx.bot.get_game(ctx.channel.id)
        if game.is_active():
            # game is active (has started)
            return True
        else:
            raise CustomCheckFailure("Game has not started yet")
    return commands.check(predicate)

def game_not_started():
    '''
    Checks that the game has not started yet
    '''
    async def predicate(ctx):
        game = ctx.bot.get_game(ctx.channel.id)
        if not game.is_active():
            # game is not active (has not started)
            return True
        else:
            raise CustomCheckFailure("Game has already started")
    return commands.check(predicate)

def is_player():
    '''
    Checks that the message author is a Player in the game
    '''
    async def predicate(ctx):
        game = ctx.bot.get_game(ctx.channel.id)
        if game.is_player(ctx.author.id):
            # author is a player in the game
            return True
        else:
            raise CustomCheckFailure("You are not a player in this game")
    return commands.check(predicate)

def is_turn():
    '''
    Checks that it is the message author's turn.
    Used as a check for all turn Actions, since it requires it
    to be the calling player's turn

    NOTE: also makes sure that it is either ACTION_STAGE for
    current turn author, or any stage but ACTION_STAGE for the
    next turn player as long as the game is not pending some action
    '''
    async def predicate(ctx):
        game = ctx.bot.get_game(ctx.channel.id)
        if game.get_stage() == CoupGame.ACTION_STAGE:
            # must be the current player
            player = game.get_turn()
        elif game.turn_can_complete():
            # must be the next player, and turn can complete
            player = game.get_next_turn()
        else:
            raise CustomCheckFailure("It is not your turn")

        # Return whether the player is valid
        if player.get_id() == ctx.author.id and player.life_count() > 0:
            return True
        else:
            raise CustomCheckFailure("It is not your turn")
    return commands.check(predicate)

def others_in_game(num_to_check, action_str):
    '''
    Checks that the @mentioned players are in the game, and that
    the @mentioned players cannot be the author
    num_to_check: int, representing how many @mentions to check
    action_str: str, representing the verb for the action being done
    '''
    async def predicate(ctx):
        game = ctx.bot.get_game(ctx.channel.id)
        i = 0
        mentions = ctx.message.mentions
        while i < len(mentions) and i < num_to_check:
            member = mentions[i]
            if ctx.author.id == member.id:
                raise CustomCheckFailure(f"You can't {action_str} yourself")
            elif not game.is_player(member.id):
                raise CustomCheckFailure(f"{member.mention} is not part of this game")
            i += 1
        return True
    return commands.check(predicate)

def is_stage(game_stage):
    '''
    Checks if the game is in the provided game stage
    '''
    async def predicate(ctx):
        game = ctx.bot.get_game(ctx.channel.id)
        return (game_stage == game.get_stage())
    return commands.check(predicate)

def is_game_master():
    '''
    Checks that the author is the game master
    '''
    async def predicate(ctx):
        game = ctx.bot.get_game(ctx.channel.id)
        if game.is_master(ctx.author.id):
            # author is the game master
            return True
        else:
            raise CustomCheckFailure("Must be game master to complete this action")
    return commands.check(predicate)

def has_enough_coins(min_coins):
    '''
    Checks if the author has enough coins to do an action
    '''
    async def predicate(ctx):
        game = ctx.bot.get_game(ctx.channel.id)
        player = game.get_player(ctx.author.id)
        if player.get_coins() >= min_coins:
            return True
        else:
            raise CustomCheckFailure("Not enough coins")
    return commands.check(predicate)

def under_ten_coins():
    '''
    Checks if the author has over 10 coins
    '''
    async def predicate(ctx):
        # Check coin count
        game = ctx.bot.get_game(ctx.channel.id)
        player = game.get_player(ctx.author.id)
        if player.get_coins() < 10:
            return True
        else:
            raise CustomCheckFailure("Over 10 coins; must coup another player")
    return commands.check(predicate)

def must_swap():
    '''
    Checks if the author needs to swap cards
    '''
    async def predicate(ctx):
        # Check if the player needs to swap a card
        game = ctx.bot.get_game(ctx.channel.id)
        player = game.get_player(ctx.author.id)
        if player.must_swap:
            return True
        else:
            raise CustomCheckFailure("You do not have to swap a card")
    return commands.check(predicate)

def must_kill():
    '''
    Checks if the author needs to kill some of their cards
    '''
    async def predicate(ctx):
        # Check if the player needs to kill a card
        game = ctx.bot.get_game(ctx.channel.id)
        player = game.get_player(ctx.author.id)
        if player.must_kill > 0:
            return True
        else:
            raise CustomCheckFailure("You do not have to kill a card")
    return commands.check(predicate)

def is_exchange():
    '''
    Makes sure that the action in the game is an Exchange, and the
    player calling the command is the one who made it.
    '''
    async def predicate(ctx):
        action = ctx.bot.get_game(ctx.channel.id).action
        if action is None or not isinstance(action, actions.Exchange):
            raise CustomCheckFailure("Action is not an `Exchange`")
        elif action.done_by.get_id() != ctx.author.id:
            raise CustomCheckFailure("You are not swapperman")
        else:
            return True
    return commands.check(predicate)

def exchange_time_up(time_up):
    '''
    Checks that if the action in the game is an Exchange, the time is up/not up.
    Assumes that the action is an Exchange (otherwise automatically passes check)
    time_up: bool, representing whether time_up should be True or False
    '''
    async def predicate(ctx):
        action = ctx.bot.get_game(ctx.channel.id).action
        if action is None or not isinstance(action, actions.Exchange):
            # Not an Exchange - assume passes check
            return True
        elif action.time_is_up() == time_up:
            # Values match
            return True
        else:
            # Values for time_up do not match
            if time_up:
                raise CustomCheckFailure("Time to challenge `Exchange` is not up")
            else:
                raise CustomCheckFailure("Time to challenge `Exchange` is already up")
    return commands.check(predicate)

def not_swapped_yet():
    '''
    Checks that the Exchange swap has not occurred yet
    '''
    async def predicate(ctx):
        action = ctx.bot.get_game(ctx.channel.id).action
        if action.has_swapped():
            raise CustomCheckFailure("Already swapped")
        else:
            return True
    return commands.check(predicate)





"""
def channel_has_game():
    '''
    Checks that the channel has a game
    '''
    async def predicate(ctx):
        if ctx.bot.get_game(ctx.channel.id) is not None:
            # channel has a game
            return True
        else:
            raise CustomCheckFailure("No active game in this channel")
    return commands.check(predicate)

def game_is_started():
    '''
    Checks that the game has actually started
    '''
    async def predicate(ctx):
        game = ctx.bot.get_game(ctx.channel.id)
        if game is None:
            raise CustomCheckFailure("No active game in this channel")
        if game.is_active():
            # game is active (has started)
            return True
        else:
            raise CustomCheckFailure("Game has not started yet")
    return commands.check(predicate)

def game_not_started():
    '''
    Checks that the game has not started yet
    '''
    async def predicate(ctx):
        game = ctx.bot.get_game(ctx.channel.id)
        if game is None:
            raise CustomCheckFailure("No active game in this channel")
        if not game.is_active():
            # game is not active (has not started)
            return True
        else:
            raise CustomCheckFailure("Game has already started")
    return commands.check(predicate)

def is_player():
    '''
    Checks that the message author is a Player in the game
    '''
    async def predicate(ctx):
        game = ctx.bot.get_game(ctx.channel.id)
        if game is None:
            raise CustomCheckFailure("No active game in this channel")
        if game.is_player(ctx.author.id):
            # author is a player in the game
            return True
        else:
            raise CustomCheckFailure("You are not a player in this game")
    return commands.check(predicate)

def is_turn():
    '''
    Checks that it is the message author's turn.
    Used as a check for all turn Actions, since it requires it
    to be the calling player's turn

    NOTE: also makes sure that it is either ACTION_STAGE for
    current turn author, or any stage but ACTION_STAGE for the
    next turn player as long as the game is not pending some action
    '''
    async def predicate(ctx):
        game = ctx.bot.get_game(ctx.channel.id)
        if game is None or not game.is_active():
            raise CustomCheckFailure("No active game in this channel")
        if game.pending and game.get_stage() == CoupGame.ACTION_STAGE:
            # must be the current player
            player = game.get_turn()
        elif not game.pending and game.get_stage != CoupGame.ACTION_STAGE:
            # must be the next player
            player = game.get_next_turn()
        else:
            raise CustomCheckFailure("It is not your turn")

        # Return whether the player is valid
        if player.get_id() == ctx.author.id and player.life_count() > 0:
            return True
        else:
            raise CustomCheckFailure("It is not your turn")
    return commands.check(predicate)

def others_in_game(num_to_check, action_str):
    '''
    Checks that the @mentioned players are in the game, and that
    the @mentioned players cannot be the author
    num_to_check: int, representing how many @mentions to check
    action_str: str, representing the verb for the action being done
    '''
    async def predicate(ctx):
        game = ctx.bot.get_game(ctx.channel.id)
        if game is None or not game.is_active():
            raise CustomCheckFailure("No active game in this channel")

        i = 0
        mentions = ctx.message.mentions
        while i < len(mentions) and i < num_to_check:
            member = mentions[i]
            if ctx.author.id == member.id:
                raise CustomCheckFailure(f"You can't {action_str} yourself")
            elif not game.is_player(member.id):
                raise CustomCheckFailure(f"{member.mention} is not part of this game")
            i += 1
        return True
    return commands.check(predicate)

def is_stage(game_stage):
    '''
    Checks if the game is in the provided game stage
    '''
    async def predicate(ctx):
        game = ctx.bot.get_game(ctx.channel.id)
        if game is None or not game.is_active():
            raise CustomCheckFailure("No active game in this channel")
        stage = game.get_stage()
        return (stage == game_stage)
    return commands.check(predicate)

def is_game_master():
    '''
    Checks that the author is the game master
    '''
    async def predicate(ctx):
        game = ctx.bot.get_game(ctx.channel.id)
        if game is None:
            raise CustomCheckFailure("No active game in this channel")
        if game.is_master(ctx.author.id):
            # author is the game master
            return True
        else:
            raise CustomCheckFailure("Must be game master to complete this action")
    return commands.check(predicate)

def has_enough_coins(min_coins):
    '''
    Checks if the author has enough coins to do an action
    '''
    async def predicate(ctx):
        # Basic checks
        game = ctx.bot.get_game(ctx.channel.id)
        if game is None:
            raise CustomCheckFailure("No active game in this channel")
        player = game.get_player(ctx.author.id)
        if player is None:
            raise CustomCheckFailure("You are not a player in this game")

        if player.get_coins() >= min_coins:
            return True
        else:
            raise CustomCheckFailure("Not enough coins")
    return commands.check(predicate)

def under_ten_coins():
    '''
    Checks if the author has over 10 coins
    '''
    async def predicate(ctx):
        # Basic checks
        game = ctx.bot.get_game(ctx.channel.id)
        if game is None:
            raise CustomCheckFailure("No active game in this channel")
        player = game.get_player(ctx.author.id)
        if player is None:
            raise CustomCheckFailure("You are not a player in this game")

        # Check coin count
        if player.get_coins() < 10:
            return True
        else:
            raise CustomCheckFailure("Over 10 coins; must coup another player")
    return commands.check(predicate)
"""