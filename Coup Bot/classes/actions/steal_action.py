'''
File: steal_action.py
Author: Gavin Vogt
This program defines the Steal action for Coup
'''

# my code
from classes.actions import Action

class Steal(Action):
    '''
    This class represents a Steal Action in the game of Coup,
    where a Captain takes 2 coins from another player
    '''

    REQUIRED_CARDS = {'captain': 1}
    AVAILABLE_RESPONSES = ["block", "pass", "challenge"]

    def __init__(self, player1, player2):
        '''
        Constructs the action
        player1: Player representing the player who is stealing
        player2: Player representing the player being stolen from
        '''
        super().__init__(player1, player2)
        if self._done_to.get_coins() >= 2:
            self._num_coins_taking = 2
        else:
            self._num_coins_taking = 1

    @staticmethod
    def is_influence_power():
        '''
        Checks if this Action can be challenged
        '''
        # steal can be challenged
        return True

    @staticmethod
    def is_blockable():
        '''
        Checks if this Action can be responded to
        '''
        # steal can be responded to
        return True

    @staticmethod
    def requires_response():
        '''
        Checks if a Response is required for gameplay to continue,
        whether the response comes as a Challenge or a Pass
        '''
        return True

    @staticmethod
    def can_block_with(influence):
        '''
        Checks if the given influence card can block this Action
        '''
        return (influence == "captain" or influence == "ambassador")

    @staticmethod
    def cost():
        '''
        Gets the cost of the steal action in coins
        '''
        return 0

    def wins_challenge(self):
        '''
        Checks if the claimed Captain wins the challenge
        '''
        return self._done_by.has("captain")

    def perform_action(self):
        '''
        Performs an action to the player(s)
        '''
        # transfer coins to the Captain
        self._done_by.add_coins(self._num_coins_taking)
        self._done_to.add_coins(-self._num_coins_taking)

    def undo_action(self):
        '''
        Undoes the action to the player(s)
        '''
        # return coins to the player
        self._done_by.add_coins(-self._num_coins_taking)
        self._done_to.add_coins(self._num_coins_taking)

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
        return f"{self._done_by.get_user().mention} attempts to yoink {self._num_coins_taking} of {self._done_to.get_user().mention}'s coins"

    def complete_message(self):
        '''
        Gets the string representing the message for when
        the action is completed successfully
        '''
        return f"{self._done_by.get_user().mention} yoinked {self._num_coins_taking} of {self._done_to.get_user().mention}'s coins"

