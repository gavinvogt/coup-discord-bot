'''
File: exchange_action.py
Author: Gavin Vogt
This program defines the Exchange action for Coup
'''

# my code
from classes.actions import Action

class Exchange(Action):
    '''
    This class represents a Exchange Action in the game of Coup,
    where an Ambassador looks at two cards in the pile and swaps
    '''

    REQUIRED_CARDS = {'ambassador': 1}
    AVAILABLE_RESPONSES = ["challenge"]
    AMBASSADOR_WAIT_TIME = 8  # waits 8 seconds before allowing ambassador

    def __init__(self, player):
        '''
        Constructs the action
        player: Player representing the player who is exchanging
        '''
        super().__init__(player)
        self._time_up = False
        self._cards = [None, None]
        self._swapped = False      # whether swap has occurred

    @staticmethod
    def is_influence_power():
        '''
        Checks if this Action can be challenged
        '''
        # exchange can be challenged
        return True

    @staticmethod
    def is_blockable():
        '''
        Checks if this Action can be responded to
        '''
        # exchange cannot be responded to
        return False

    @staticmethod
    def requires_response():
        '''
        Checks if a Response is required for gameplay to continue,
        whether the response comes as a Challenge or a Pass
        '''
        return False

    @staticmethod
    def can_block_with(influence):
        '''
        Checks if the given influence card can block this Action
        '''
        return False

    @staticmethod
    def cost():
        '''
        Gets the cost of the exchange action in coins
        '''
        return 0

    @classmethod
    def get_wait_time(cls):
        '''
        Gets the number of seconds that must pass before the action can continue
        '''
        return cls.AMBASSADOR_WAIT_TIME

    def set_time_up(self, time_up):
        '''
        Sets whether the time is up
        time_up: bool, representing whether the time to challenge is up
        '''
        self._time_up = time_up

    def time_is_up(self):
        '''
        Checks if the time is up (can no longer challenge)
        '''
        return self._time_up

    def has_swapped(self):
        '''
        Checks if the card swap has already occurred
        '''
        return self._swapped

    def perform_swap(self, player_card, i, game):
        '''
        Performs the card swap and shuffles the pile
        player_card: int, representing the index of the player's card they are swapping.
        If `player_card` is None, represents no swap taking place
        i: int, representing the index of the card to swap with
        game: CoupGame where swap is occurring
        '''
        self._swapped = True
        if player_card is not None:
            # Swap the player's card with self._cards[i]
            card = self._done_by[player_card].type
            self._done_by.set_influence(player_card, self._cards[i])
            self._cards[i] = card

        # Add cards back into pile and shuffle
        for card in self._cards:
            game.add_card(card)
        game.shuffle()

    def get_card(self, i):
        '''
        Returns the card at index `i`
        i: int, representing the index of the card to get
        Return: str, representing the influence type
        '''
        return self._cards[i]

    def set_card(self, i, card):
        '''
        Sets the card at index `i` to `card`
        i: int, representing the index of the card
        card: str, representing the influence type
        '''
        self._cards[i] = card

    def wins_challenge(self):
        '''
        Checks if the claimed Ambassador wins the challenge
        '''
        return self._done_by.has("ambassador")

    def perform_action(self):
        '''
        Performs an action to the player(s)
        '''
        self._done_by.must_swap = True

    def undo_action(self):
        '''
        Undoes the action to the player(s)
        '''
        self._done_by.must_swap = False

    @staticmethod
    def is_super():
        '''
        Checks if this Action is a super (such as Double Contessa), and
        requires a card swap either way
        '''
        return False

    @classmethod
    def available_responses(cls, channel_mention):
        '''
        Returns the embed holding available responses to
        an action
        '''
        return cls.response_embed(cls.AVAILABLE_RESPONSES, channel_mention)

    def attempt_message(self):
        '''
        Gets the string representing the message for when
        the action is attempted
        '''
        return f"{self._done_by.get_user().mention} attempts to exchange influences"

    def complete_message(self):
        '''
        Gets the string representing the message for when
        the action is completed successfully
        '''
        return f"{self._done_by.get_user().mention} exchanged influences"