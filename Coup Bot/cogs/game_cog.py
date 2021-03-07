'''
File: game_cog.py
Author: Gavin Vogt
This program creates the Game cog for the Coup Bot
'''

# dependencies
from discord import User, Embed, Color
from discord.ext import commands
import asyncio

# my code
from cogs.base_cog import BaseCog
from classes.coup_game import CoupGame
from classes import actions, responses
from helpers.command_checks import (channel_has_game, game_is_started, is_stage,
            game_not_started, is_player, is_turn,others_in_game, has_enough_coins,
            under_ten_coins, is_game_master, must_swap, must_kill, is_exchange,
            exchange_time_up, not_swapped_yet)


# Removing a player during the game
FORFEIT_HELP = "Forfeit from a game"
KICK_HELP = "Kick a player from the game"

# Action commands
STEAL_HELP = "Steal 2 coins from another player (CAPTAIN)"
EXCHANGE_HELP = "Look at two cards in the pile to exchange (AMBASSADOR)"
SWAP_HELP = "Perform the swap in an exchange"
NOSWAP_HELP = "Skipp the swap in an exchange"
ASSASSINATE_HELP = "Assassinate another player for 3 coins (ASSASSIN)"
TAX_HELP = "Take tax for +3 coins (DUKE)"
INCOME_HELP = "Take income for +1 coin (GENERAL)"
FOREIGNAID_HELP = "Take foreign aid for +2 coins (GENERAL)"
COUP_HELP = "Launch a coup on another player for 7 coins (GENERAL)"

# Response commands
PASS_HELP = "Pass on responding to another player's action"
CHALLENGE_HELP = "Challenges a player's claim"
DIE_HELP = "Select card(s) to die"
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

    async def cog_before_invoke(self, ctx):
        game = self.bot.get_game(ctx.channel.id)
        if game is not None:
            print("\nBefore:", "-"*45, game, sep='\n')
            print("-"*45)

    async def cog_after_invoke(self, ctx):
        '''
        After every command in this Cog, it will automatically check
        if the turn / game is over and advance the turn if necessary.
        '''
        game = self.bot.get_game(ctx.channel.id)
        if game is not None:
            print("\nAfter:", "-"*45, game, sep='\n')

            # Check if game / turn is over
            await self._check_turn_over(ctx.channel, game, advance_if_possible=False)
            await self._check_game_over(ctx.channel, game)

            le = game.last_event()
            if le is not None:
                print("\nLast event:", le)
                print("Wins challenge:", le.wins_challenge())
            print("-"*45)


    ################################### ACTION COMMANDS ################################

    @commands.command(name="steal", help=STEAL_HELP, aliases=['captain'])
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
        player = game.get_player(ctx.author.id)
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
        game = self.bot.get_game(ctx.channel.id)
        user = ctx.message.mentions[0]
        stealing_from = game.get_player(user.id)
        if stealing_from.get_coins() < 1:
            # user doesn't have enough coins to steal from
            await ctx.send(f"{user.mention} is too broke to steal from")
            raise commands.CheckFailure(f"{user.mention} is too broke to steal from")
        await self.pre_action_check(ctx)

    @commands.command(name="exchange", help=EXCHANGE_HELP, aliases=['ambassador'])
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
        exchange = actions.Exchange(player)
        game.action = exchange
        exchange.perform_action()
        await ctx.send(exchange.attempt_message())

        # Wait for someone to challenge before continuing
        wait_time = actions.Exchange.get_wait_time()
        wait_embed = Embed(
            title = "Waiting for challenges ...",
            description = f"{wait_time} seconds remaining",
            color = Color.orange(),
        )
        msg = await ctx.send(embed=wait_embed)
        exchange.set_time_up(False)
        await asyncio.sleep(1)
        for i in range(wait_time - 1, 0, -1):
            if game.challenge1 is not None:
                # challenge occurred; continue and see if won
                exchange.set_time_up(True)
                break
            wait_embed.description = f"{i} seconds remaining"
            await msg.edit(embed=wait_embed)
            await asyncio.sleep(1)

        # Wait is over
        exchange.set_time_up(True)
        if game.challenge1 is not None and not exchange.wins_challenge():
            # Exchange failed
            wait_embed.description = "CANCELLED"
            wait_embed.color = Color.red()
            await msg.edit(embed=wait_embed)
            await ctx.send("Exchange cancelled")
        else:
            # Carry out the exchange
            wait_embed.description = "SUCCESS"
            wait_embed.color = Color.green()
            await msg.edit(embed=wait_embed)
            await ctx.send(f"Showing {exchange.done_by.get_mention()} top 2 cards")

            # Draw the top two cards
            exchange.set_card(0, game.draw_card())
            exchange.set_card(1, game.draw_card())
            card_embed = Embed(
                title = "Top Two Cards",
                description = "Use `c!hand` if you need to see your hand.\nSelect a card to swap with:",
                color = Color.green(),
            )
            card_embed.set_footer(text="c!swap <yourCardIndex> <otherCardIndex>\nc!noswap")
            card_embed.add_field(name="Card 1", value=exchange.get_card(0).capitalize())
            card_embed.add_field(name="Card 2", value=exchange.get_card(1).capitalize())

            await exchange.done_by.get_user().send(embed=card_embed)

    @commands.command(name="swap", help=SWAP_HELP)
    @exchange_time_up(True)
    @not_swapped_yet()
    @is_exchange()
    @must_swap()
    @is_player()
    @game_is_started()
    @channel_has_game()
    @commands.guild_only()
    async def perform_card_swap(self, ctx, your_card: int, swap_with: int):
        '''
        Lets the user perform a card swap to finish the Exchange
        your_card: index of player's card to swap
        swap_with: index of exchange card to swap with
        '''
        game = self.bot.get_game(ctx.channel.id)
        player = game.get_player(ctx.author.id)

        # Verify that the indices are valid
        your_card -= 1
        swap_with -= 1
        if not (0 <= your_card < game.influences_per_player()):
            await ctx.send(f"Invalid index: `your_card={your_card + 1}`")
            return
        if not player[your_card].alive:
            await ctx.send(f"Your card `{your_card + 1}` is not alive")
            return
        if not (0 <= swap_with <= 1):
            await ctx.send(f"Invalid index: `swap_with={swap_with + 1}`")
            return

        # Perform the swap
        await player.get_user().send(f"Swapped your `{player[your_card].type.capitalize()}`, for `{game.action.get_card(swap_with).capitalize()}`")
        game.action.perform_swap(your_card, swap_with, game)
        player.must_swap = False
        await ctx.send("Performed swap and shuffled draw pile")

        await self._check_turn_over(ctx.channel, game, advance_if_possible=True)

    @commands.command(name="noswap", help=NOSWAP_HELP)
    @exchange_time_up(True)
    @not_swapped_yet()
    @is_exchange()
    @must_swap()
    @is_player()
    @game_is_started()
    @channel_has_game()
    @commands.guild_only()
    async def no_card_swap(self, ctx):
        '''
        Lets the user decide not to swap cards
        '''
        game = self.bot.get_game(ctx.channel.id)
        player = game.get_player(ctx.author.id)

        game.action.perform_swap(None, 0, game)
        player.must_swap = False
        await ctx.send("Skipped swap and shuffled draw pile")

        await self._check_turn_over(ctx.channel, game, advance_if_possible=True)

    @commands.command(name="assassinate", help=ASSASSINATE_HELP, aliases=['assassin'])
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
        await user.send(embed=game.action.available_responses(ctx.channel.mention))

    @commands.command(name="tax", help=TAX_HELP, aliases=['duke'])
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
        await ctx.send(embed=game.action.available_responses(ctx.channel.mention))

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
        await user.send(embed=game.action.available_responses(ctx.channel.mention))

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
            await ctx.send(f"{game.action.done_by.get_mention()}'s action is not blockable")
            return
        elif not isinstance(game.action, actions.ForeignAid) and \
                game.action.done_to is not player:
            # not foreign aid, so block must be by `done_to` player
            await ctx.send(f"Only {game.action.done_to.get_mention()} is allowed to block")
            return
        elif player is player_to_block:
            # tried to block self
            await ctx.send("You can't block yourself")
            return

        # Auto determine the influence if necessary
        influence = influence.lower()
        if influence == "auto-determine":
            # automatically determine what influence they are using to block
            if isinstance(game.action, actions.Assassinate):
                # blocking assassination with Contessa
                influence = "contessa"
            elif isinstance(game.action, actions.ForeignAid):
                # blocking foreign aid with Duke
                influence = "duke"
            elif isinstance(game.action, actions.LaunchCoup):
                # blocking coup with Double Contessa
                influence = "doublecontessa"
            elif isinstance(game.action, actions.Steal):
                # blocking a steal with either Captain or Ambassador, but didn't specify
                await ctx.send("Please specify whether you are blocking with Captain or Ambassador")
                return

        # Make sure the block is possible with the given card
        if not game.action.can_block_with(influence):
            await ctx.send(f"`{influence.capitalize()}` is unable to block {player_to_block.get_mention()}'s action")
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

        # Perform the block by undoing the action
        game.action.undo_action()

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
        if action.done_to is not None and ctx.author.id == action.done_to.get_id():
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

        # Pass means the game is no longer pending
        game.pending = False

    @commands.command(name="challenge", help=CHALLENGE_HELP)
    @exchange_time_up(False)
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

                # Create and carry out the challenge (automatically undoes the action)
                challenge = responses.Challenge(player, player_to_challenge)
                game.action.undo_action()
                await ctx.send(challenge.attempt_message())
                if game.action.done_to is not None and ctx.author.id == game.action.done_to.get_id():
                    # user is responding with Challenge -> store as response
                    game.response = challenge
                else:
                    # general user challenging -> store as challenge1
                    game.challenge1 = challenge
                await self.handle_challenge(ctx, game, game.action, challenge)
            else:
                await ctx.send(f"Can't challenge {game.action.done_by.get_mention()}'s action")
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
                await ctx.send(f"Can't challenge {game.response.response_by.get_mention()}'s action")
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
            await ctx.send(f"{challenged.get_mention()} won the challenge!")
            if isinstance(action, actions.Action):
                # person who made Action won; redo the action
                action.perform_action()
            # if isinstance(action, Response): don't do anything because action was already undone
            challenger.must_kill += 1

            # Automatically swap challenged_player's revealed card
            await self._handle_swap(ctx.channel, game, challenged, action, revealed=True)
            action.swapped = True
        else:
            # Action was a bluff (challenger wins)
            await ctx.send(f"{challenger.get_mention()} won the challenge!")
            if isinstance(action, actions.Action):
                pass
                # challenger won against person who made Action; undo the action
                # ACTION HAS ALREADY BEEN UNDONE
            if isinstance(action, responses.Response):
                # challenger won against person who made Response; redo action that had been blocked
                game.action.perform_action()

            challenged.must_kill += 1

    @commands.command(name="die", help=DIE_HELP)
    @must_kill()
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

        # Figure out which cards to kill
        try:
            card_indexes = {int(num) - 1 for num in card_nums}
            if len(card_indexes) != player.must_kill:
                # they aren't killing the correct number
                await ctx.send(f"Need to kill `{player.must_kill}` cards, try again")
                return
            for i in card_indexes:
                if not player[i].alive:
                    # tried to kill a card that wasn't alive
                    await ctx.send(f"Card `{i + 1}` is not alive, try again")
                    return
        except:
            await ctx.send(f"Card `{i + 1}` is not valid, try again")
            return

        # Create and perform the action
        response = responses.Die(player, *card_indexes)
        response.perform_action()
        game.add_death(response)
        await ctx.send(response.complete_message())

        # Check if the player is eliminated
        if player.is_eliminated():
            await self.bot.process_player_remove(ctx.channel, game, player)
            await ctx.send(f"{ctx.author.mention} was eliminated")


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
        if game.is_active():
            player = game.get_player(user.id)

            # Kill their cards
            cards_killed = []
            for i in range(game.influences_per_player()):
                card = player[i]
                if card.alive:
                    game.add_to_dead_pile(card.type)
                    cards_killed.append(card.type.capitalize())
            if len(cards_killed) > 0:
                await ctx.send(f"{user.mention}'s {', '.join(cards_killed)} was killed")

            await self.bot.process_player_remove(ctx.channel, game, player)
        else:
            # game hasn't started yet
            game.unsign_up_player(user.id)
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
            player = game.get_player(ctx.author.id)
            await ctx.send(ctx.author.mention + " left the game")

            # Kill their cards
            cards_killed = []
            for i in range(game.influences_per_player()):
                card = player[i]
                if card.alive:
                    game.add_to_dead_pile(card.type)
                    cards_killed.append(card.type.capitalize())
            if len(cards_killed) > 0:
                await ctx.send(f"{ctx.author.mention}'s {', '.join(cards_killed)} was killed")

            await self.bot.process_player_remove(ctx.channel, game, player)


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
            return await self._check_turn_over(channel, game, send_prompt=False)
        # was not their turn
        return False

    async def _check_turn_over(self, channel, game, *, advance_if_possible=True, send_prompt=True):
        '''
        Checks if the current turn is over for the given game. If the turn
        is over, it automatically wraps up the turn and advances it
        channel: discord.Channel where game is being played
        game: CoupGame representing the game
        advance_if_possible: bool, representing whether to advance the turn on the
        sole basis that it is "possible"
        send_prompt: bool, representing whether to send prompts after
        rotating the turn (defaults to False)
        Return: True if the turn was completed, and False otherwise
        '''
        if game.soft_pending and not advance_if_possible:
            # game is soft pending and don't need to advance if necessary
            if not game.hard_pending and game.action is not None:
                await channel.send(f"Respond, or {game.get_next_turn().get_mention()} is next up")
            return
        elif game.is_over():
            # Send the last turn summary
            await channel.send(embed=game.turn_summary())
            return
        elif game.hard_pending:
            # Send which specific players have pending moves
            await channel.send(embed=game.pending_players_embed())
            return False
        elif game.turn_can_complete():
            # Swap cards for any supers used
            await self._check_super_swaps(channel, game)

            # Send turn summary and advance to next turn
            await channel.send(embed=game.turn_summary())
            game.next_turn()
            if send_prompt:
                # Prompt user for their action
                await channel.send(f"It is now {game.get_turn().get_mention()}'s turn")
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
            await channel.send(f"Game over - {winner.get_mention()} was victorious 🎉")
            self.bot.remove_game(channel.id)
            return True
        else:
            return False

    async def _check_super_swaps(self, channel, game):
        '''
        Checks if any automatic swaps need to happen. Only happens for
        cards that are "supers" (like Double Contessa)
        channel: Channel to send information to
        game: CoupGame to check swaps for
        '''
        # Check for swapping in the Action
        action = game.action
        if action is not None and action.is_super() and not action.swapped:
            # Action was a super and has not been swapped yet
            await self._handle_swap(channel, game, action.done_by, action, revealed=False)

        # Check for swapping in the Response
        response = game.response
        if response is not None and response.is_super() and not response.swapped:
            # Response was a super and has not been swapped yet
            await self._handle_swap(channel, game, response.response_by, response, revealed=False)

    async def _handle_swap(self, channel, game, player, action, *, revealed):
        '''
        Handles a card swap for the player in the given game, for the given action. The
        action informs the method which cards need to be swapped
        channel: Channel to send information to
        game: CoupGame for the game being played
        player: Player getting their cards swapped
        action: Action or Response that needs to be swapped for
        revealed: bool, whether the cards were revealed
        '''
        swapped_cards = game.swap_cards(player, action.REQUIRED_CARDS.copy())  # CardSwap object
        if revealed:
            card_text = swapped_cards.in_text()
        else:
            maybe_swapped = []
            for influence_type, num in action.REQUIRED_CARDS.items():
                for _ in range(num):
                    maybe_swapped.append(influence_type.capitalize())
            card_text = f"(maybe) `{'`, `'.join(maybe_swapped)}`"
        await channel.send(f"Swapped {player.get_mention()}'s revealed {card_text} for new cards")
        await player.get_user().send(swapped_cards.summary_text())
        action.swapped = True


def setup(bot):
    bot.add_cog(GameCog(bot))
