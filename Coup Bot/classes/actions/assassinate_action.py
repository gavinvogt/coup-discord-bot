'''
File: assassinate_action.py
Author: Gavin Vogt
This program defines the Assassinate action for Coup
'''

# my code
from classes.actions import Action

class Assassinate(Action):
    '''
    This class represents an Assassinate Action in the game of Coup,
    performed by an assassin to another player
    '''

    REQUIRED_CARDS = {'assassin': 1}
    AVAILABLE_RESPONSES = ["block", "die", "challenge"]

    def __init__(self, player1, player2):
        '''
        Constructs the action
        player1: Player representing the player who is doing the assassination
        player2: Player representing the player who is being assassinated
        '''
        super().__init__(player1, player2)
        self._new_coins = player1.get_coins() - self.cost()

    @staticmethod
    def is_influence_power():
        '''
        Checks if this Action can be challenged
        '''
        # assassination can be challenged
        return True

    @staticmethod
    def is_blockable():
        '''
        Checks if this Action can be blocked by the acted-on user
        '''
        # assassination can be responded to
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
        return (influence == "contessa")

    @staticmethod
    def cost():
        '''
        Gets the cost of the assassination in coins
        '''
        return 3

    def wins_challenge(self):
        '''
        Checks if the claimed Assassin wins the challenge
        '''
        return self._done_by.has("assassin")

    def perform_action(self):
        '''
        Performs an action to the player(s)
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
        return f"{self._done_by.get_user().mention} attempts to assassinate {self._done_to.get_user().mention}"

    def complete_message(self):
        '''
        Gets the string representing the message for when
        the action is completed successfully
        '''
        return f"{self._done_by.get_user().mention} assassinated {self._done_to.get_user().mention}"