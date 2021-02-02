'''
File: game_cog.py
Author: Gavin Vogt
This program creates the Game cog for the Coup Bot
'''

# dependencies
from discord import User
from discord.ext import commands

# my code
from cogs.base_cog import BaseCog
from classes.coup_game import CoupGame
from classes import actions
from classes import responses
from helpers.command_checks import (channel_has_game, game_is_started, is_stage,
            game_not_started, is_player, is_turn,others_in_game, has_enough_coins,
            under_ten_coins, is_game_master)


# Removing a player during the game
FORFEIT_HELP = "Forfeit from a game"
KICK_HELP = "Kick a player from the game"

# Action commands
STEAL_HELP = "Steal 2 coins from another player (CAPTAIN)"
EXCHANGE_HELP = "Look at two cards in the pile to exchange (AMBASSADOR)"
ASSASSINATE_HELP = "Assassinate another player for 3 coins (ASSASSIN)"
TAX_HELP = "Take tax for +3 coins (DUKE)"
INCOME_HELP = "Take income for +1 coin (GENERAL)"
FOREIGNAID_HELP = "Take foreign aid for +2 coins (GENERAL)"
COUP_HELP = "Launch a coup on another player for 7 coins (GENERAL)"

# Response commands
PASS_HELP = "Pass on responding to another player's action"
CHALLENGE_HELP = "Challenges a player's claim"
BLOCK_HELP = """Blocks another player's action
Valid influence types:
  - contessa
  - captain
  - ambassador
  - duke
  - doublecontessa
"""


class GameCog(BaseCog, name="game"):
    '''
    Commands for setting up and playing a game of Coup
    '''
    def __init__(self, bot):
        super().__init__(bot)

    """
    async def cog_before_invoke(self, ctx):
        '''
        Rotates the turn before the command is run, if necessary
        '''
        # Make sure the game properly rotates the turn
        game = self.bot.get_game(ctx.channel.id)
        player = game.get_player(ctx.author.id)
        await self._check_turn_rotation(ctx.channel, game, player)
    """

    async def cog_after_invoke(self, ctx):
        '''
        After every command in this Cog, it will automatically check
        if the turn / game is over and advance the turn if necessary.
        '''
        game = self.bot.get_game(ctx.channel.id)
        if game is not None:
            await self._check_turn_over(ctx.channel, game)
            await self._check_game_over(ctx.channel, game)


    ################################### ACTION COMMANDS ################################

    @commands.command(name="steal", help=STEAL_HELP)
    @others_in_game(1, "steal from")
    @under_ten_coins()
    @has_enough_coins(actions.Steal.cost())
    @is_turn()
    @is_player()
    @game_is_started()
    @channel_has_game()
    @commands.guild_only()
    async def steal_from_player(self, ctx, user: User):
        '''
        Steals from another player
        user: discord.User of player to steal from
        '''
        # Get the game and other player
        game = self.bot.get_game(ctx.channel.id)
        other_player = game.get_player(user.id)

        # Create and perform the Action
        game.action = actions.Steal(player, other_player)
        game.action.perform_action()
        await ctx.send(game.action.attempt_message())
        await user.send(embed=game.action.available_responses(ctx.channel.mention))

    @steal_from_player.before_invoke
    async def before_steal_from_player(self, ctx):
        '''
        Before a steal, it checks that the player has at least 1 coin
        and rotates the turn if necessary
        '''
        user = ctx.message.mentions[0]
        game = self.bot.get_game(ctx.channel.id)
        player = game.get_player(user.id)
        if other_player.get_coins() < 1:
            # user doesn't have enough coins to steal from
            await ctx.send(f"{user.mention} is too broke to steal from")
            raise commands.CheckFailure(f"{user.mention} is too broke to steal from")
        await self.pre_action_check(ctx)

    @commands.command(name="exchange", help=EXCHANGE_HELP)
    @under_ten_coins()
    @has_enough_coins(actions.Exchange.cost())
    @is_turn()
    @is_player()
    @game_is_started()
    @channel_has_game()
    @commands.guild_only()
    async def exchange_cards(self, ctx):
        '''
        Lets the user view the top two cards in the pile and
        swap up to one of their own cards with one from the pile
        '''
        game = self.bot.get_game(ctx.channel.id)
        player = game.get_player(ctx.author.id)

        # Create and perform the Action
        game.action = actions.Exchange(player)
        game.action.perform_action()
        await ctx.send(game.action.attempt_message())

    @commands.command(name="assassinate", help=ASSASSINATE_HELP)
    @others_in_game(1, "assassinate")
    @under_ten_coins()
    @has_enough_coins(actions.Assassinate.cost())
    @is_turn()
    @is_player()
    @game_is_started()
    @channel_has_game()
    @commands.guild_only()
    async def assassinate_player(self, ctx, user: User):
        '''
        Assassinates another player
        user: discord.User of player to assassinate
        '''
        # Get the game and other player
        game = self.bot.get_game(ctx.channel.id)
        player = game.get_player(ctx.author.id)
        other_player = game.get_player(user.id)

        # Create and perform the Action
        game.action = actions.Assassinate(player, other_player)
        game.action.perform_action()
        await ctx.send(game.action.attempt_message())
        await user.send(embed=game.action.available_responses(channel.mention))

    @commands.command(name="tax", help=TAX_HELP)
    @under_ten_coins()
    @has_enough_coins(actions.Tax.cost())
    @is_turn()
    @is_player()
    @game_is_started()
    @channel_has_game()
    @commands.guild_only()
    async def take_tax(self, ctx):
        '''
        Lets a duke take tax
        '''
        game = self.bot.get_game(ctx.channel.id)
        player = game.get_player(ctx.author.id)

        # Create and perform the Action
        game.action = actions.Tax(player)
        game.action.perform_action()
        await ctx.send(game.action.attempt_message())

    @commands.command(name="income", help=INCOME_HELP)
    @under_ten_coins()
    @has_enough_coins(actions.Income.cost())
    @is_turn()
    @is_player()
    @game_is_started()
    @channel_has_game()
    @commands.guild_only()
    async def take_income(self, ctx):
        '''
        Lets a player take income
        '''
        game = self.bot.get_game(ctx.channel.id)
        player = game.get_player(ctx.author.id)

        # Create and perform the Action
        game.action = actions.Income(player)
        game.action.perform_action()
        await ctx.send(game.action.attempt_message())

    @commands.command(name="foreignaid", help=FOREIGNAID_HELP)
    @under_ten_coins()
    @has_enough_coins(actions.ForeignAid.cost())
    @is_turn()
    @is_player()
    @game_is_started()
    @channel_has_game()
    @commands.guild_only()
    async def take_foreign_aid(self, ctx):
        '''
        Lets a player take foreign aid
        '''
        game = self.bot.get_game(ctx.channel.id)
        player = game.get_player(ctx.author.id)

        # Create and perform the Action
        game.action = actions.ForeignAid(player)
        game.action.perform_action()
        await ctx.send(game.action.attempt_message())
        await ctx.send(embed=game.action.available_responses(channel.mention))

    @commands.command(name="coup", help=COUP_HELP)
    @others_in_game(1, "coup")
    @has_enough_coins(actions.LaunchCoup.cost())
    @is_turn()
    @is_player()
    @game_is_started()
    @channel_has_game()
    @commands.guild_only()
    async def do_coup(self, ctx, user: User):
        '''
        Lets a player coup another player
        user: discord.User of player to coup
        '''
        # Get the game and other player
        game = self.bot.get_game(ctx.channel.id)
        player = game.get_player(ctx.author.id)
        other_player = game.get_player(user.id)

        # Create and perform the Action
        game.action = actions.LaunchCoup(player, other_player)
        game.action.perform_action()
        await ctx.send(game.action.attempt_message())
        await user.send(embed=game.action.available_responses(channel.mention))

    # CHECK BEFORE EACH ACTION IF THE TURN / GAME IS OVER
    # (steal not included because it has a more specific check above)
    @exchange_cards.before_invoke
    async def pre_exchange_check(self, ctx):
        await self.pre_action_check(ctx)
    @take_tax.before_invoke
    async def pre_tax_check(self, ctx):
        await self.pre_action_check(ctx)
    @assassinate_player.before_invoke
    async def pre_assassination_check(self, ctx):
        await self.pre_action_check(ctx)
    @take_income.before_invoke
    async def pre_income_check(self, ctx):
        await self.pre_action_check(ctx)
    @take_foreign_aid.before_invoke
    async def pre_foreign_aid_check(self, ctx):
        await self.pre_action_check(ctx)
    @do_coup.before_invoke
    async def pre_coup_check(self, ctx):
        await self.pre_action_check(ctx)

    async def pre_action_check(self, ctx):
        '''
        After every ACTION command in this Cog, it will automatically check
        if the turn / game is over and advance the turn if necessary.
        '''
        # Make sure the game properly rotates the turn
        game = self.bot.get_game(ctx.channel.id)
        player = game.get_player(ctx.author.id)
        await self._check_turn_rotation(ctx.channel, game, player)

    ################################## RESPONSE COMMANDS ###############################

    @commands.command(name="block", help=BLOCK_HELP)
    @commands.check_any(is_stage(CoupGame.CHALLENGE1_STAGE), is_stage(CoupGame.RESPONSE_STAGE))
    @game_is_started()
    @is_player()
    @channel_has_game()
    @commands.guild_only()
    async def block_action(self, ctx, influence="auto-determine"):
        '''
        Blocks another player's action from this turn
        influence: str, representing which influence the player is using to block
        '''
        # Get the players involved in the Reponse
        game = self.bot.get_game(ctx.channel.id)
        player = game.get_player(ctx.author.id)
        player_to_block = game.action.done_by

        # Check if player is allowed to block player_to_block
        if not game.action.is_blockable():
            # action itself cannot be blocked
            await ctx.send(f"{game.action.done_by.get_user().mention}'s action is not blockable")
            return
        elif not isinstance(game.action, actions.ForeignAid) and \
                game.action.done_to is not player:
            # not foreign aid, so block must be by `done_to` player
            await ctx.send(f"Only {game.action.done_to.get_user().mention} is allowed to block")
            return
        elif player is player_to_block:
            # tried to block self
            await ctx.send("You can't block yourself")
            return

        # Auto determine the influence if necessary
        influence = influence.lower()
        if inluence == "auto-determine":
            # automatically determine what influence they are using to block
            if isinstance(ACTION, actions.Assassinate):
                # blocking assassination with Contessa
                influence = "contessa"
            elif isinstance(ACTION, actions.ForeignAid):
                # blocking foreign aid with Duke
                influence = "duke"
            elif isinstance(ACTION, actions.ForeignAid):
                # blocking coup with Double Contessa
                influence = "doublecontessa"
            elif isinstance(ACTION, actions.Steal):
                # blocking a steal with either Captain or Ambassador, but didn't specify
                await ctx.send("Please specify whether you are blocking with Captain or Ambassador")
                return

        # Make sure the block is possible with the given card
        if not game.action.can_block_with(influence):
            await ctx.send(f"{influence.captalize()} is unable to block {player_to_block.get_user().mention}'s action")
            return

        # Convert the influence type into the correct Reponse class
        if influence == "contessa":
            response = responses.ContessaBlock(player, player_to_block)
        elif influence == "captain":
            response = responses.CaptainBlock(player, player_to_block)
        elif influence == "ambassador":
            response = responses.AmbassadorBlock(player, player_to_block)
        elif influence == "duke":
            response = responses.DukeBlock(player, player_to_block)
        elif influence == "doublecontessa":
            response = responses.DoubleContessaBlock(player, player_to_block)
        else:
            await ctx.send("""```Please name a valid influence to block with:
  - contessa
  - captain
  - ambassador
  - duke
  - doublecontessa```""")
            return

        # set the game's Response stage to the newly created response
        game.response = response
        await ctx.send(response.attempt_message())

    @commands.command(name="pass", help=PASS_HELP)
    @commands.check_any(
        is_stage(CoupGame.CHALLENGE1_STAGE),
        is_stage(CoupGame.RESPONSE_STAGE),
        is_stage(CoupGame.CHALLENGE2_STAGE))
    @game_is_started()
    @is_player()
    @channel_has_game()
    @commands.guild_only()
    async def pass_response(self, ctx):
        '''
        Lets a player pass on responding, allowing the other
        player's Action or Response to go through successfully

        Done by action.done_to:
            - during `challenge1` stage, forcing through to `response` stage
            - during the `response` stage after some other player challenged and lost.
        Done by action.done_by:
            - during `challenge2` stage, allowing other player's Response to go through
        '''
        # Make sure `pass` is an option
        game = self.bot.get_game(ctx.channel.id)
        action = game.action
        if (action is None) or (not action.is_blockable()):
            # there was no choice between blocking / challenging and passing
            await ctx.send("Nothing to pass on")
            return
        game_stage = game.get_stage()

        # done_to user responding
        if ctx.author.id == action.done_to.get_id():
            # must be `challenge1` or `response` stage
            if game_stage == CoupGame.CHALLENGE1_STAGE or game_stage == CoupGame.RESPONSE_STAGE:
                # Allows the Action to complete unchecked (turn ends)
                game.response = responses.Pass(action.done_to, action.done_by)
                await ctx.send(game.response.attempt_message())
            else:
                return

        # done_by user responding to a Block
        elif ctx.author.id == action.done_by.get_id():
            # must be `challenge2` stage
            if game_stage == CoupGame.CHALLENGE2_STAGE:
                # Allows the (Block) Response to go through
                response = game.response
                game.challenge2 = responses.Pass(response.response_to, response.response_by)
                await ctx.send(game.challenge2.attempt_message())
            else:
                return

        # done by a general user
        else:
            await ctx.send("You are unable to pass")
            return

    @commands.command(name="challenge", help=CHALLENGE_HELP)
    @commands.check_any(is_stage(CoupGame.CHALLENGE1_STAGE), is_stage(CoupGame.CHALLENGE2_STAGE))
    @game_is_started()
    @is_player()
    @channel_has_game()
    @commands.guild_only()
    async def challenge_player(self, ctx):
        '''
        Challenges the last user who did an action
        '''
        game = self.bot.get_game(ctx.channel.id)
        player = game.get_player(ctx.author.id)
        game_stage = game.get_stage()

        # Check which event is being challenged
        if game_stage == CoupGame.CHALLENGE1_STAGE:
            # challenging the Action
            if game.action.is_influence_power():
                player_to_challenge = game.action.done_by
                if ctx.author.id == player_to_challenge.get_id():
                    # trying to challenge themself
                    await ctx.send("You can't challenge yourself")
                    return

                # Create and carry out the challenge
                challenge = responses.Challenge(player, player_to_challenge)
                await ctx.send(challenge.attempt_message())
                if ctx.author.id == game.action.done_to.get_id():
                    # user is responding with Challenge -> store as response
                    game.response = challenge
                else:
                    # general user challenging -> store as challenge1
                    game.challenge1 = challenge
                await self.handle_challenge(ctx, game, game.action, challenge)

                # TODO : separate into `setup` and `game` cogs
            else:
                await ctx.send(f"Can't challenge {game.action.done_by.get_user().mention}'s action")
                return

        elif game_stage == CoupGame.CHALLENGE2_STAGE:
            # challenging the Response
            if game.response.is_influence_power():
                player_to_challenge = game.response.response_by
                if ctx.author.id == player_to_challenge.get_id():
                    # trying to challenge themself
                    await ctx.send("You can't challenge yourself")
                    return
                else:
                    # create and carry out the Challenge
                    game.challenge2 = responses.Challenge(player, player_to_challenge)
                    await ctx.send(game.challenge2.attempt_message())
                    await self.handle_challenge(ctx, game, game.response, game.challenge2)
            else:
                await ctx.send(f"Can't challenge {game.response.response_by.get_user().mention}'s action")
                return

    async def handle_challenge(self, ctx, game, action, challenge):
        '''
        Handles the given challenge by checking the result
        ctx: Context to send results to
        game: CoupGame holding the game
        action: Action or Response being challenged
        challenge: Challenge that was issued
        '''
        challenged = challenge.response_to
        challenger = challenge.response_by
        if action.wins_challenge():
            # Action was valid (challenged player wins)
            await ctx.send(f"{challenged.get_user().mention} won the challenge!")
            challenger.must_kill += 1

            # Automatically swap challenged_player's revealed card
            game.swap_cards(challenged, action.REQUIRED_CARDS)
            await ctx.send(f"Swapped {challenged.get_user()}'s revealed cards for new ones")
        else:
            # Action was a bluff (challenger wins)
            await ctx.send(f"{challenger.get_user().mention} won the challenge!")
            action.undo_action()
            challenged.must_kill += 1

    @commands.command(name="die")
    @is_player()
    @game_is_started()
    @channel_has_game()
    @commands.guild_only()
    async def select_death(self, ctx, *card_nums):
        '''
        Allows player to select their card to die
        card_num: int, representing the numerical index of their
        card they are choosing to let die (indexed from 0)
        '''
        game = self.bot.get_game(ctx.channel.id)
        player = game.get_player(ctx.author.id)

        # Check if the player needs to kill a card
        if not player.must_kill > 0:
            # player does not have to kill a card
            await ctx.send("You do not have to kill a card")
            return

        # Figure out which cards to kill
        try:
            card_indexes = {int(num) - 1 for num in card_nums}
            if len(card_indexes) != player.must_kill:
                # they aren't killing the correct number
                await ctx.send(f"Need to kill `{player.must_kill}` cards, try again")
            for i in card_indexes:
                if not player[i].alive:
                    # tried to kill a card that wasn't alive
                    await ctx.send(f"Card `{i + 1}` is not alive, try again")
        except:
            await ctx.send(f"Card `{i + 1}` is not valid, try again")
            return

        # TODO: it doesn't know if killing a card is a Response, such as to an assassination
        # or a required action
        response = responses.Die(player, *card_indexes)

        # TODO: add to game.[turn_stage]

        # TODO: do the action
        response.perform_action()
        await ctx.send(response.complete_message())


    ############################## REMOVING PLAYERS FROM GAME ##############################

    @commands.command(name="kick", help=KICK_HELP)
    @others_in_game(1, "kick")  # checks that other player is part of game and not self
    @is_game_master()
    @channel_has_game()
    @commands.guild_only()
    async def kick_player(self, ctx, user: User):
        '''
        Allows the game master to kick a player from the game
        user: User to kick
        '''
        # Possible to kick player if checks are passed
        game = self.bot.get_game(ctx.channel.id)
        game.remove_player(user.id)
        self.bot.set_user_status(user.id, False)
        await ctx.send(f"Removed {user.mention} from game")

    @commands.command(name="forfeit", help=FORFEIT_HELP)
    @is_player()
    @channel_has_game()
    @commands.guild_only()
    async def forfeit_game(self, ctx):
        '''
        Allows a user to forfeit from a game that has already started
        '''
        game = self.bot.get_game(ctx.channel.id)
        if not game.is_active():
            await ctx.send(f"Please use `{self.bot.command_prefix}leave` to leave the game")
        elif game.player_count() == 1:
            # Last player is leaving game; delete game
            self.bot.set_user_status(user.id, False)
            self.bot.remove_game(channel_id)
            await ctx.send("No players remain - game cancelled")
        else:
            game.remove_player(ctx.author.id)
            self.bot.set_user_status(user.id, False)
            await ctx.send(ctx.author.mention + " left the game")
            await self.bot.transfer_master(game, ctx.author.id)

        # TODO
        # Action and Response classes might have text they return
        # to say stuff for if challenge won/lost or if action completed


    ################################# HELPER METHODS ###############################

    async def _prompt_response(self, channel, game):
        '''
        Helper method that prompts the player for their response to
        another player's move
        channel: discord.Channel to send response prompt in
        game: CoupGame object representing the game being played
        '''
        # Find what is being responded to
        if game.challenge2 is not None:
            responding_to = game.challenge2
            if game.response.wins_challenge():
                player = game.challenge2.response_by  # player who challenged must respond
            else:
                player = game.challenge2.response_to  # player who was challenged must respond
        elif game.response is not None:
            responding_to = game.response
            player = responding_to.response_to
        elif game.challenge1 is not None:
            responding_to = game.challenge1
            if game.action.wins_challenge():
                player = game.challenge1.response_by  # player who challenged must respond
            else:
                player = game.challenge1.response_to  # player who was challenged must respond
        elif game.action is not None:
            responding_to = game.action
            player = responding_to.done_to

        if not (responding_to.is_influence_power() or responding_to.is_blockable()):
            # Nothing to respond to
            return

        if player is None:
            # asking for general responses
            await channel.send(
                "Waiting for general response ...",
                embed=responding_to.available_responses(channel.mention))
        else:
            # asking user sepecifically
            await channel.send(f"Waiting for {player.get_mention()}'s response ...")
            await player.get_user().send(embed=responding_to.available_responses(channel.mention))

    async def _check_turn_rotation(self, channel, game, player):
        '''
        Checks the turn rotation. If the provided player is the current
        turn player, nothing happens. If the provided player is the
        next turn player, the game's previous turn must be finished up,
        and then updated for a new turn.
        channel: discord.Channel to send any messages to
        game: CoupGame object holding the game
        player: Player object holding the player who made a command
        Return: True if turn rotated, False otherwise
        '''
        if game.get_next_turn().get_id() == player.get_id():
            # player is from the next turn
            return self._check_turn_over(channel, game, send_prompt=False)
        # was not their turn
        return False

    async def _check_turn_over(self, channel, game, *, send_prompt=True):
        '''
        Checks if the current turn is over for the given game. If the turn
        is over, it automatically wraps up the turn and advances it
        channel: discord.Channel where game is being played
        game: CoupGame representing the game
        send_prompt: bool, representing whether to send prompts after
        rotating the turn (defaults to False)
        Return: True if the turn was completed, and False otherwise
        '''
        if game.hard_pending:
            # Send which specific players have pending moves
            await channel.send(embed=game.pending_players_embed())
            return False
        elif game.turn_can_complete():
            # Send turn summary and advance to next turn
            await channel.send(embed=game.turn_summary())
            game.next_turn()
            if send_prompt:
                # Prompt user for their action
                await channel.send(f"It is now {game.get_turn().get_user().mention}'s turn")
                await self.bot.prompt_action(channel)
            return True

    async def _check_game_over(self, channel, game):
        '''
        Checks if the given game is over. If it is over, sends the
        appropriate message to the game channel
        channel: discord.Channel to send game over message to
        game: CoupGame object representing game to check
        Return: True if the game was over, False otherwise
        '''
        # Check if the game is over
        if game.is_over():
            # game has a winner
            winner = game.get_winner()
            await ctx.send(f"{winner.get_user().mention} was victorious!")
            self.bot.remove_game(channel_id)
            return True
        else:
            return False



def setup(bot):
    bot.add_cog(GameCog(bot))
