'''
File: coup_game.py
Author: Gavin Vogt
This program defines the CoupGame class, which is used
to represent a game of Coup
'''

# dependencies
from discord import Embed, Color
from datetime import datetime
import random

# my code
from classes.player import Player
from classes.card_swap import CardSwap
from helpers.display_utils import ordered_list

class CoupGame:
    '''
    This class represents a game of Coup, which can be customized with
    varying player count limits, start coins, and start influences.

    Public fields:
        - action
        - challenge1
        - response
        - challenge2

    The game is set up in two major phases:
        Signup phase (self.is_active() = False):
            - Keep track of who will be playing
        Gameplay phase (self.is_active() = True):
            - Create a Player object for every player
            - Create the turn order and select the player to go first
            - Play the game
    '''

    MIN_PLAYERS_DEFAULT = 2   # also acts as a hard min
    MAX_PLAYERS_DEFAULT = 6
    HARD_MAX_PLAYERS = 12

    START_COINS_DEFAULT = 2
    START_INFLUENCES_DEFAULT = 2
    CARD_TYPES = ('contessa', 'captain', 'ambassador', 'assassin', 'duke')
    ACTION_TYPES = ('steal', 'exchange', 'assassinate', 'tax', 'income', 'foreignaid', 'coup')

    # values representing the stages within a turn
    ACTION_STAGE = 0
    CHALLENGE1_STAGE = 1
    RESPONSE_STAGE = 2
    CHALLENGE2_STAGE = 3
    COMPLETE_STAGE = 4    # when the turn completes, and any cleanup needs to be done

    def __init__(self, master_id, *, min_players=None, max_players=None,
            start_coins=None, start_influences=None, card_count=None):
        '''
        Constructs a new game
        master_id: user ID of the game master (person who started game)
        min_players: int, representing the min players in game
        max_players: int, representing the max players in game
        start_coins: int, representing the number of coins players start with
        start_influences: int, representing the number of influence cards to start with
        card_count: int, representing the total number of cards in the game
        '''
        # Used during game setup
        self._signup_ids = {}      # maps signed up player IDs to discord.User
        self._master = master_id   # who is running the game
        self._active = False       # whether the game is active
        self._created_at = datetime.utcnow()

        # Game settings
        self._set_player_constraints(min_players, max_players)
        self._set_start_settings(start_coins, start_influences)
        self._set_preferred_cards(card_count)

        # Used during game play
        self._players = {}         # dict of user_id : Player
        self._draw_pile = []       # list of cards, where last card is the "top"
        self._dead_pile = {}       # maps card type to count
        self._total_cards = 0

        # Information about the turn rotation
        self._order = []           # game rotation order as list of user IDs
        self._turn = 0             # index of player whose turn it is

        # Turn stage: 0 (action), 1 (challenge), 2 (response), 3 (challenge)
        # Creates variables: _stage, _action, _challenge1, _response, _challenge2, _pending
        self.clean_turn_vars()

    def __repr__(self):
        '''
        String representing the game settings
        '''
        attr_names = ('_master', '_min_players', '_max_players', '_start_coins', '_start_influences')
        attrs = ", ".join([f"{attr.lstrip('_')}={getattr(self, attr)}" for attr in attr_names])
        return f"{self.__class__.__name__}({attrs})"

    def __str__(self):
        '''
        String representing the current game state
        '''
        return "\n".join((
            f"Active: {self._active}",
            f"Player count: {self.player_count()}",
            f"Stage: {self._stage}",
            f"Can complete: {self.turn_can_complete()}",
            f"Last event: {self.last_event()}",
            f"Soft pending: {self.soft_pending}",
            f"Hard pending: {self.hard_pending}",
            f"Pending: {self.pending}",
        ))

    @property
    def soft_pending(self):
        '''
        If the game is "soft pending" it is waiting for OPTIONAL responses,
        but can move on at any time
        '''
        return self._pending

    @property
    def hard_pending(self):
        '''
        If the game is "hard pending" it is waiting for REQUIRED responses,
        and cannot move on until they are fulfilled
        '''
        return len(self.get_pending_players()) > 0

    @property
    def pending(self):
        '''
        Gives access to the `pending` property, which checks whether the
        game is waiting for some kind of action (may or may not be able to continue,
        see the `soft_pending` and `hard_pending` properties
        '''
        return (self._pending or len(self.get_pending_players()) > 0)

    @pending.setter
    def pending(self, pending_val):
        '''
        Setter for the `pending` property, which checks whether the
        game is waiting for some kind of action before it can continue
        '''
        self._pending = pending_val

    @property
    def action(self):
        '''
        Gives access to the `action` property
        '''
        return self._action

    @action.setter
    def action(self, new_action):
        '''
        Setter for the `action` property
        Automatically advances `stage` to the proper stage,
        and sets whether the game is `pending` any actions
        '''
        # Set to the action
        self._action = new_action

        # Set the turn stage
        if new_action.is_influence_power():
            # advance stage to `challenge1`
            self._stage = self.CHALLENGE1_STAGE
            self._pending = True
        elif new_action.is_blockable():
            # advance stage to `response`
            self._stage = self.RESPONSE_STAGE
            self._pending = True
        else:
            # the action can go through immediately (no challenges or blocks)
            self._stage = self.COMPLETE_STAGE
            self._pending = False

    @property
    def challenge1(self):
        '''
        Gives access to the `challenge1` property
        '''
        return self._challenge1

    @challenge1.setter
    def challenge1(self, new_challenge):
        '''
        Setter for the `challenge1` property
        Automatically advances `stage` to the proper stage,
        and sets whether the game is `pending` any actions
        '''
        # Set the stage
        self._challenge1 = new_challenge
        if self._action.wins_challenge():
            # player who did Action would win challenge
            if self._action.done_to is not None and \
                    new_challenge.response_by.get_id() == self._action.done_to.get_id():
                # challenge won against responding player -- turn over
                self._stage = self.COMPLETE_STAGE
            else:
                # challenge won against general player
                if self._action.is_blockable():
                    # block by done_to player is still available
                    self._stage = self.RESPONSE_STAGE
                else:
                    # blocking is not available -- turn over
                    self._stage = self.COMPLETE_STAGE
        else:
            # player who did Action would lose challenge
            self._stage = self.COMPLETE_STAGE

        # Either way, game is now pending one player to kill one of their cards
        self._pending = True

    @property
    def response(self):
        '''
        Gives access to the `response` property
        '''
        return self._response

    @response.setter
    def response(self, new_response):
        '''
        Setter for the `response` property
        Automatically advances `stage` to the proper stage,
        and sets whether the game is `pending` any actions
        '''
        self._response = new_response
        if new_response.is_influence_power():
            # can be challenged; advance stage to `challenge2`
            self._stage = self.CHALLENGE2_STAGE
            self._pending = True
        else:
            # response cannot be challenged
            self._stage = self.COMPLETE_STAGE
            self._pending = False

    @property
    def challenge2(self):
        '''
        Gives access to the `challenge2` property
        '''
        return self._challenge2

    @challenge2.setter
    def challenge2(self, new_challenge):
        '''
        Setter for the `challenge2` property
        Automatically advances `stage` to the proper stage,
        and sets whether the game is `pending` any actions
        '''
        self._challenge2 = new_challenge
        self._stage = self.COMPLETE_STAGE  # challenge2 automatically ends turn

        # Either way, game is now pending one player to kill one of their cards
        self._pending = True

    def initialize_game(self):
        '''
        Initializes the game so it is ready to play:
            - Sets as active
            - Randomizes turn order
            - Fills and shuffles card pile
            - Creates Player objects and deals cards

        Up to the user to set whose turn it is with set_turn(player_id)
        '''
        # Fill the card pile and shuffle it
        self._fill_card_pile()
        self.shuffle()

        # Set game to `active` state
        self._active = True

        # Initialize all the players
        for user_id, user in self._signup_ids.items():
            # give player their user ID / mention, start coins, and start influences
            player = Player(user, self._start_coins, self._start_influences)
            for i in range(self._start_influences):
                # Draw a card and give it to the player
                player.set_influence(i, self.draw_card())
            self._players[user_id] = player
            self._order.append(user_id)

        # Randomize the turn order
        self.randomize_order()


    ########################## GAME STATE METHODS #####################

    def get_min(self):
        '''
        Gets the max number of players for the game
        '''
        return self._min_players

    def get_max(self):
        '''
        Gets the max number of players for the game
        '''
        return self._max_players

    def is_active(self):
        '''
        Checks if the game is active (has been started)
        '''
        return self._active

    def player_count(self):
        '''
        Gets the number of players in the game
        '''
        if self.is_active():
            return len(self._players)
        else:
            return len(self._signup_ids)

    def influences_per_player(self):
        '''
        Gets the number of influence cards each player starts with
        '''
        return self._start_influences

    def get_master(self):
        '''
        Getter for the user ID of the game master
        '''
        return self._master

    def is_master(self, user_id):
        '''
        Checks if the given user is the game master
        user_id: int, representing the ID of the player to check
        '''
        return (user_id == self._master)

    def is_valid(self):
        '''
        Checks if the game is valid to start. Must be between
        minimum and maximum player counts
        '''
        return (self.get_min() <= self.player_count() <= self.get_max())

    def is_over(self):
        '''
        Checks if the game is over (1 player remaining)
        '''
        return self.is_active() and (self.player_count() <= 1)

    def get_winner(self):
        '''
        Returns the Player object of the game winner
        '''
        return self._players[self._order[0]]

    def shuffle(self):
        '''
        Shuffles the cards in the draw pile
        '''
        random.shuffle(self._draw_pile)


    ############################ SIGNUP STAGE #########################

    def is_signed_up(self, user_id):
        '''
        Checks if a player is signed up for the game
        user_id: int, representing the player's Discord ID
        '''
        return (user_id in self._signup_ids)

    def sign_up_player(self, user):
        '''
        Signs up a player for the game
        user: discord.User object holding the user signing up
        '''
        self._signup_ids[user.id] = user

    def unsign_up_player(self, user_id):
        '''
        Removes a player's signup
        user_id: int, representing the player's Discord ID
        '''
        if user_id in self._signup_ids:
            del self._signup_ids[user_id]


    ############################## GAMEPLAY STAGE ###########################

    def get_player(self, user_id):
        '''
        Gets the player in this game with the given user ID
        user_id: int, representing the player's Discord ID
        Return: Player object if the user in this game, otherwise None
        '''
        return self._players.get(user_id)

    def get_players(self):
        '''
        Gets all of the players in the game as a list
        '''
        return list(self._players.values())

    def remove_player(self, user_id):
        '''
        Removes a player from the game by deleting them from the dictionary
        of players and fixing the turn order.
        user_id: int, representing the ID of the player to remove
        Return: True if it was that player's turn at the time, and False otherwise
        '''
        if user_id in self._players.keys():
            del self._players[user_id]

            # Remove the player from the turn order, and possibly change turn
            i = self._order.index(user_id)
            self._order.pop(i)
            if i == self._turn:
                # Turn was that of current player
                self._turn -= 1  # subtract so next_turn() increments it to the correct player
                self.next_turn()
                return True      # let caller know it was that player's turn
        return False             # let caller know it was not that player's turn

    def get_stage(self):
        '''
        Gets the stage of the current turn
        '''
        return self._stage

    def add_dead(self, card_type):
        '''
        Adds a card to the pile of dead
        '''
        if card_type in self._dead_pile:
            self._dead_pile[card_type] += 1
        else:
            self._dead_pile[card_type] = 1

    def randomize_order(self):
        '''
        Randomizes the player order
        '''
        random.shuffle(self._order)

    def randomize_turn(self):
        '''
        Randomizes whose turn it is
        '''
        self._turn = random.randint(0, self.player_count() - 1)

    def clean_turn_vars(self):
        '''
        Cleans up the turn variables as a clean slate to prepare
        for the next turn
        '''
        # keep track of the stage and previous actions
        self._stage = self.ACTION_STAGE
        self._action = None
        self._challenge1 = None
        self._response = None
        self._challenge2 = None

        # Keep track of any deaths this turn
        self._deaths = []    # list of Die responses

        # whether the game is pending an action / response / other to continue
        # to the next turn
        self._pending = True

    def next_turn(self):
        '''
        Sets the game to the next turn
        '''
        # Advance the turn variable
        self._turn += 1
        if self._turn > (self.player_count() - 1):
            self._turn = 0

        # Clean up all the players' must_kill and must_swap values
        for player in self._players.values():
            player.must_kill = 0
            player.must_swap = False

        # Reset the stage / action / challenge1 / response / challenge2 fields
        self.clean_turn_vars()

    def get_turn(self):
        '''
        Gets the Player whose turn it is
        '''
        user_id = self._order[self._turn]
        return self._players[user_id]

    def get_next_turn(self):
        '''
        Gets the Player whose turn is next
        '''
        next_turn = self._turn + 1
        if next_turn > (self.player_count() - 1):
            next_turn = 0

        user_id = self._order[next_turn]
        return self._players[user_id]

    def turn_can_complete(self):
        '''
        Checks whether the turn is able to complete
        Return: True if the turn can end now, and False otherwise
        '''
        if self.hard_pending:
            # still pending some REQUIRED action
            return False
        elif self._stage == self.COMPLETE_STAGE:
            # complete stage and not hard pending
            return True
        else:
            # can end turn as long as an action has been made
            return (self.action is not None)

    def last_event(self):
        '''
        Gets the last event that was done in this game
        Return: Action or Response object that was done last, or None if N/A
        '''
        for attr_name in ('challenge2', 'response', 'challenge1', 'action'):
            event = getattr(self, attr_name, None)
            if event is not None:
                # found the latest event
                return event
        # no events have occurred
        return None

    def set_turn_to(self, player_id):
        '''
        Sets the turn to be the given player
        player_id: user ID of the player to set turn to
        '''
        self._turn = self._order.index(player_id)

    def turn_summary(self):
        '''
        Generates an embed summarizing the turn
        '''
        turn_embed = Embed(
            title = "Turn Summary",
            color = Color.teal(),
            timestamp = datetime.utcnow(),
        )

        # Summarize the actions, challenges, and responses of the game
        if self._action is not None:
            turn_embed.add_field(name="Action", value=self._action.complete_message(), inline=False)
        if self._challenge1 is not None:
            turn_embed.add_field(name="Challenge 1", value=self._challenge1.complete_message(), inline=False)
        if self._response is not None:
            turn_embed.add_field(name="Response", value=self._response.complete_message(), inline=False)
        if self._challenge2 is not None:
            turn_embed.add_field(name="Challenge 2", value=self._challenge2.complete_message(), inline=False)

        if len(self._deaths) > 0:
            turn_embed.add_field(name="Deaths", value="\n".join(d.complete_message() for d in self._deaths))

        turn_embed.set_footer(text="Turn completed at")
        return turn_embed

    def print_summary(self):
        '''
        Prints out the game summary
        '''
        print(repr(self))
        print("Action:", self._action)
        print("Challenge 1:", self._challenge1)
        print("Response:", self._response)
        print("Challenge 2:", self._challenge2)
        print("-"*45)
        print("CURRENT TURN:", self.get_turn())
        print("DRAW PILE:", self._draw_pile)
        print("-"*45)
        for player in self._players.values():
            print(repr(player), ":")
            for i in range(self._start_influences):
                print("    -", player[i])

    def add_card(self, card):
        '''
        Adds a card to the top of the pile
        '''
        self._draw_pile.append(card)

    def draw_card(self):
        '''
        Draws a card from the pile (removing it)
        '''
        # The last card in the list is the "top" of the pile
        card = self._draw_pile.pop()
        return card

    def swap_cards(self, player, cards_to_swap):
        '''
        Swaps the player's cards with random cards from the draw pile
        player: Player to swap cards with
        cards_to_swap: dict of {influence_type: num to swap}
        Return: CardSwap object representing the cards that were swapped in/out
        '''
        # Check if the player has all the required cards
        has_all = True
        num_to_swap = 0
        for influence_type, num in cards_to_swap.items():
            num_to_swap += num
            has_all &= player.has(influence_type, num)

        # Add the right cards back into the draw pile
        influences = player.get_influences()
        indices_to_swap = []
        swapped_in = []

        if has_all:
            # player has all the cards for the swap
            for i in range(len(influences)):
                influence = influences[i]
                if influence is not None and influence.alive:
                    cur_num_to_swap = cards_to_swap.get(influence.type, 0)
                    if cur_num_to_swap > 0:
                        # Add the card to the draw pile
                        self._draw_pile.append(influence.type)
                        swapped_in.append(influence)
                        indices_to_swap.append(i)
                        cards_to_swap[influence.type] -= 1
        else:
            # just try to swap the right number
            for i in range(num_to_swap):
                influence = influences[i]
                if influence is not None and influence.alive:
                    # Add the card to the draw pile
                    self._draw_pile.append(influence.type)
                    swapped_in.append(influence)
                    indices_to_swap.append(i)
                    num_to_swap -= 1

        # Shuffle the cards and draw to replace
        self.shuffle()
        swapped_for = []
        for index in indices_to_swap:
            drew = self.draw_card()
            swapped_for.append(drew)
            player.set_influence(index, drew)

        return CardSwap(swapped_in, swapped_for)

    def get_pending_players(self):
        '''
        Gets the list of players with a pending action, such as
        a player that needs to kill at least one of their cards
        or do an ambassador swap
        '''
        pending_players = []
        for player in self._players.values():
            if player.must_kill > 0 or player.must_swap:
                pending_players.append(player)
        return pending_players

    def pending_players_embed(self):
        '''
        Gets the embed representing which players have pending actions,
        and for what reason
        '''
        pending_embed = Embed(
            title = "Pending Actions",
            description = "Awaiting actions from the following players:",
            color = Color.orange(),
        )
        if self.action is None:
            # Waiting for player to make their Action
            player = self.get_turn()
            pending_embed.add_field(name="Waiting for Action ...", value=player.get_mention(), inline=False)
        elif self.response is None and self.action.done_to is not None:
            # Waiting for affected player to respond
            pending_embed.add_field(name="Waiting for Response ...", value=self.action.done_to.get_mention(), inline=False)
        for player in self.get_pending_players():
            pending_embed.add_field(name="Player", value=player.get_mention())
            pending_embed.add_field(name="Must Kill", value=player.must_kill)
            pending_embed.add_field(name="Must Swap Cards", value=player.must_swap)
        return pending_embed

    def setup_embed(self, channel_mention):
        '''
        Generates the embed representing the settings for the game
        '''
        setup_embed = Embed(
            title = 'Game Settings',
            timestamp = self._created_at,
        )

        # General game information
        setup_embed.add_field(name="Channel", value=channel_mention)
        setup_embed.add_field(name="Game Master", value=self._signup_ids[self._master].mention)
        if self.is_active():
            setup_embed.color = Color.green()
            mentions = ordered_list([player.get_mention() for player in self._players.values()])
        else:
            setup_embed.color = Color.orange()
            mentions = ordered_list([user.mention for user in self._signup_ids.values()])
        setup_embed.add_field(name="Current Players", value=mentions)

        # Gameplay settings
        setup_embed.add_field(name="Start Coins", value=self._start_coins)
        setup_embed.add_field(name="Start Lives", value=self._start_influences)
        setup_embed.add_field(name="Status", value='🟢 Started 🟢' if self._active else '🟠 Not started 🟠')

        # Information about player counts
        setup_embed.add_field(name="Player count", value=self.player_count())
        setup_embed.add_field(name="Min players", value=self._min_players)
        setup_embed.add_field(name="Max players", value=self._max_players)

        setup_embed.set_footer(text="Created at")
        return setup_embed

    @staticmethod
    def rules_embed(prefix=None):
        '''
        Creates the embed representing the game rules
        prefix: str, representing the bot prefix
        '''
        rules_embed = Embed(
            title = "Coup Rules",
            description = "At the start of their turn, the player can perform one action. Other players may block, challenge, or let the action pass. A block to a response may also be challenged.\nIf a player has over 10 coins, they are required to coup this turn.",
            color = Color.blue(),
        )
        rules_embed.add_field(name="Contessa", value="`Block assassination`")
        rules_embed.add_field(name="Double Contessa", value="`Block coup`")
        rules_embed.add_field(name="Assassin", value="`Assassinate (-3 coins)`")
        rules_embed.add_field(name="Captain", value="`Steal (+2 coins)`\n`Block steal`")
        rules_embed.add_field(name="Ambassador", value="`Exchange cards`\n`Block steal`")
        rules_embed.add_field(name="Duke", value="`Tax (+3 coins)`\n`Block foreign aid`")
        rules_embed.add_field(name="(General Ability)", value="`Income (+1 coin)`\n`Foreign aid (+2 coins)`\n`Coup (-7 coins)`\n`Challenge action`")
        if prefix is not None:
            rules_embed.set_footer(text=f"See {prefix}guide for gameplay guide")
        return rules_embed

    def summary_embed(self):
        '''
        Generates the embed showing the game summary, which
        includes the turn order, current turn, number of influences
        each player has, and their coin counts
        '''
        # Set up the embed
        summary_embed = Embed(
            title = "Game Summary",
            description = f"Total cards: {self._total_cards}",
            color = Color.green(),
        )

        # Add information for each user
        mentions = []
        life_counts = []
        coin_counts = []
        for i in range(len(self._order)):
            # Get the player
            player_id = self._order[i]
            player = self._players[player_id]

            # Add the player's information that is visible to everyone
            life_counts.append(str(player.life_count()))
            coin_counts.append(str(player.get_coins()))
            if i == self._turn:
                # bold stats of player whose turn it is
                mentions.append(f"⭐ **{player.get_mention()}**")
                life_counts[-1] = "**" + life_counts[-1] + "**"
                coin_counts[-1] = "**" + coin_counts[-1] + "**"
            else:
                mentions.append(f"{i + 1}. {player.get_mention()}")
        summary_embed.add_field(name="Player 🃏", value="\n".join(mentions))
        summary_embed.add_field(name="Lives ❤", value="\n".join(life_counts))
        summary_embed.add_field(name="Coins 🪙", value="\n".join(coin_counts))

        if len(self._deaths) > 0:
            summary_embed.add_field(name="Deaths", value="\n".join(d.complete_message() for d in self._deaths))

        return summary_embed

    def add_death(self, die_response):
        '''
        Adds a death that occurred during the turn. If it makes it so the
        game will no longer be hard pending, automatically sets `pending`
        to false and updates the game stage.
        '''
        if self.response is None:
            # player used Die as their response
            self.response = die_response
        else:
            # player was forced to use Die
            self._deaths.append(die_response)

        # Add to dead pile
        for card_type in die_response.get_killed():
            self.add_to_dead_pile(card_type)

        # Check pending status
        if not self.hard_pending:
            self._stage = self.COMPLETE_STAGE
            self.pending = False

    def add_to_dead_pile(self, card_type):
        '''
        Adds a card type to the dead pile
        '''
        # accidentally re-wrote a method and used it; not worth to fix it
        self.add_dead(card_type)

    def dead_embed(self):
        '''
        Generates an embed showing all the dead cards
        '''
        dead_pile_embed = Embed(
            title = "Dead Pile",
            color = Color.red(),
        )
        description = "```"
        for card_type, dead_count in self._dead_pile.items():
            description += f"{card_type.capitalize()} (x{dead_count})" + "\n"
        dead_pile_embed.description = description + " ```"
        return dead_pile_embed

    @classmethod
    def is_valid_card(cls, card_type):
        '''
        Checks if the given card is valid
        '''
        return (card_type.lower() in cls.CARD_TYPES)


    ########################### HYBRID METHODS #######################

    def is_player(self, user_id):
        '''
        Checks if the given user is a player in the game (either signed
        up or actually playing if the game has started)
        user_id: int, representing the player's discord ID
        '''
        if self.is_active():
            # game has started; check if in game
            return (self.get_player(user_id) is not None)
        else:
            # game has not started; check if signed up
            return self.is_signed_up(user_id)

    def get_player_ids(self):
        '''
        Returns the user ID for every player in the game. If the game
        has started, returns IDs of players still in the game. If still
        in signup stage, returns IDs of signed up players
        '''
        if self.is_active():
            # game has started
            return list(self._players.keys())
        else:
            # list of player IDs for players signed up for game
            return list(self._signup_ids.keys())

    def random_player(self):
        '''
        Chooses a random player in the game
        Return: discord.User object of the player
        '''
        if self.is_active():
            # getting a random player still in game
            player_id = random.choice(list(self._players.keys()))
            return self._players[player_id].get_user()
        else:
            # getting a random signed up player
            player_id = random.choice(list(self._signup_ids.keys()))
            return self._signup_ids[player_id]

    def set_master(self, user_id):
        '''
        Attempts to set a new game master
        user_id: int, representing the ID of the player to elevate to game master
        Return: True if successful, False otherwise
        '''
        if not self.is_active() and user_id in self._signup_ids:
            # game hasn't started, and player is signed up
            self._master = user_id
            return True
        elif self.is_active() and user_id in self._players:
            # game has started, and player is still in game
            self._master = user_id
            return True
        else:
            # Can't make a non-player the game master
            return False

    @classmethod
    def possible_actions_embed(cls, channel_mention):
        actions_embed = Embed(
            title = "Available Actions",
            description = "``` - " + "\n - ".join(cls.ACTION_TYPES) + "```",
            color = Color.green(),
        )
        actions_embed.add_field(name="Channel", value=channel_mention)
        return actions_embed


    ########################## HELPER METHODS ##########################

    def _set_player_constraints(self, min_players, max_players):
        '''
        Helper method for setting the constraints on the number
        of players in the game
        '''
        # Constraint on minimum number of players
        if min_players is None or min_players < self.MIN_PLAYERS_DEFAULT:
            self._min_players = self.MIN_PLAYERS_DEFAULT
        else:
            self._min_players = min_players

        # Constraint on maximum number of players
        if max_players is None:
            self._max_players = self.MAX_PLAYERS_DEFAULT
        elif max_players < self._min_players:
            # max players must be >= min players
            self._max_players = self._min_players
        elif max_players > self.HARD_MAX_PLAYERS:
            # max players must be below hard max
            self._max_players = self.HARD_MAX_PLAYERS
        else:
            self._max_players = max_players

    def _set_start_settings(self, start_coins, start_influences):
        '''
        Helper method for setting up the number of starting coins
        and starting influence cards in the game
        '''
        # Set start coins
        if start_coins is None or start_coins < 0:
            # start coins must be at least 0
            self._start_coins = self.START_COINS_DEFAULT
        else:
            self._start_coins = start_coins

        # Set number of starting influence cards
        if start_influences is None or start_influences < 1:
            # start influences must be at least 1
            self._start_influences = self.START_INFLUENCES_DEFAULT
        else:
            self._start_influences = start_influences

    def _set_preferred_cards(self, card_count):
        '''
        Sets up the preferred card count for the game.
        Restrictions:
            - must be a multiple of len(self.CARD_TYPES) which should be 5
        '''
        if card_count is None:
            self._preferred_card_count = None
        else:
            # must be a factor of 5 (number of card types)
            num_types = len(self.CARD_TYPES)
            mod = card_count % 5
            if mod == 0:
                # valid number of cards
                self._preferred_card_count = card_count
            else:
                # round up to nearest 5 count
                self._preferred_card_count = card_count + (num_types - mod)

    def _fill_card_pile(self):
        '''
        Adds all of the cards to the draw pile (NOT SHUFFLED)
        '''
        # Need at over 2 larger than (cards per player X player count)
        num_needed = self._start_influences * self.player_count() + 3
        num_types = len(self.CARD_TYPES)
        if self._preferred_card_count is not None and self._preferred_card_count >= num_needed:
            count_per_card = int(self._preferred_card_count / num_types)
        else:
            mod = num_needed % num_types
            if mod == 0:
                # exactly a multiple of num_types
                count_per_card = int(num_needed / num_types)
            else:
                # get to the next multiple of num_types
                count_per_card = int((num_needed + num_types - mod) / num_types)

        # Add all the cards to the pile (NOT SHUFFLED)
        for card_type in self.CARD_TYPES:
            for _ in range(count_per_card):
                self._draw_pile.append(card_type)

        # Set number of total cards
        self._total_cards = len(self._draw_pile)