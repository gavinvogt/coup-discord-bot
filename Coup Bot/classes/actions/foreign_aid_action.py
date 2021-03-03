'''
File: foreign_aid_action.py
Author: Gavin Vogt
This program defines the ForeignAid action for Coup
'''

# my code
from classes.actions import Action

class ForeignAid(Action):
    '''
    This class represents an ForeignAid Action in the game of Coup,
    performed by any player to draw 2 coins but can be blocked by dukes
    '''

    REQUIRED_CARDS = {}
    AVAILABLE_RESPONSES = ["block"]

    def __init__(self, player):
        '''
        Constructs the action
        player: Player representing the player taking foreign aid
        '''
        super().__init__(player)

    @staticmethod
    def is_influence_power():
        '''
        Checks if this Action can be challenged
        '''
        # foreign aid cannot be challenged
        return False

    @staticmethod
    def is_blockable():
        '''
        Checks if this Action can be responded to
        '''
        # foreign aid can be responded to by a duke
        return True

    @staticmethod
    def requires_response():
        '''
        Checks if a Response is required for gameplay to continue,
        whether the response comes as a Challenge or a Pass
        '''
        # can be blocked, but passing is implicit
        return False

    @staticmethod
    def can_block_with(influence):
        '''
        Checks if the given influence card can block this Action
        '''
        return (influence == "duke")

    @staticmethod
    def cost():
        '''
        Gets the cost of the foreign aid action in coins
        '''
        return 0

    def wins_challenge(self):
        '''
        Checks if the player wins the challenge
        '''
        # general command can be done by anyone
        return True

    def perform_action(self):
        '''
        Performs an action to the player(s)
        '''
        # give the player 2 coins
        self._done_by.add_coins(2)

    def undo_action(self):
        '''
        Undoes the action to the player(s)
        '''
        self._done_by.add_coins(-2)

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
        return f"{self._done_by.get_user().mention} attempts to take foreign aid of 2 coins"

    def complete_message(self):
        '''
        Gets the string representing the message for when
        the action is completed successfully
        '''
        return f"{self._done_by.get_user().mention} took foreign aid of 2 coins"
