'''
File: coup_action.py
Author: Gavin Vogt
This program defines the LaunchCoup action for Coup
'''

# my code
from classes.actions import Action

class LaunchCoup(Action):
    '''
    This class represents a LaunchCoup Action in the game of Coup,
    performed by any player to launch a coup on another for 7 coins
    '''

    REQUIRED_CARDS = {}
    AVAILABLE_RESPONSES = ["block", "die"]

    def __init__(self, player1, player2):
        '''
        Constructs the action
        player1: Player representing the player doing the coup
        player2: Player representing the player being couped
        '''
        super().__init__(player1, player2)
        self._new_coins = player1.get_coins() - self.cost()

    @staticmethod
    def is_influence_power():
        '''
        Checks if this Action can be challenged
        '''
        # coup cannot be challenged
        return False

    @staticmethod
    def is_blockable():
        '''
        Checks if this Action can be responded to
        '''
        # coup can be responded to by Double Contessa
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
        return (influence == "doublecontessa")

    @staticmethod
    def cost():
        '''
        Gets the cost of the launch coup action in coins
        '''
        return 7

    def wins_challenge(self):
        '''
        Checks if the player wins the challenge
        '''
        # general command can be done by anyone
        return True

    def perform_action(self):
        '''
        Performs an action to the player
        '''
        self._done_by.set_coins(self._new_coins)
        self._done_to.must_kill += 1

    def undo_action(self):
        '''
        Undoes the action to the player(s)
        '''
        # Player doesn't get coins back
        self._done_to.must_kill -= 1

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
        return f"{self._done_by.get_user().mention} launches a coup on {self._done_to.get_user().mention}"

    def complete_message(self):
        '''
        Gets the string representing the message for when
        the action is completed successfully
        '''
        return f"{self._done_by.get_user().mention} couped {self._done_to.get_user().mention}"