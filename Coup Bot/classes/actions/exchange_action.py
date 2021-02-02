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

    def __init__(self, player):
        '''
        Constructs the action
        player: Player representing the player who is exchanging
        '''
        super().__init__(player)

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

    def wins_challenge(self):
        '''
        Checks if the claimed Ambassador wins the challenge
        '''
        return self._done_by.has("ambassador")

    def perform_action(self):
        '''
        Performs an action to the player(s)
        '''
        #self._done_by

        TODO

    def undo_action(self):
        '''
        Undoes the action to the player(s)
        '''
        TODO

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



