'''
File: challenge.py
Author: Gavin Vogt
This program defines the Challenge reponse in Coup, where
a player challenges another player's Action
'''

# my code
from classes.responses import Response

class Challenge(Response):
    '''
    This class represents a Challenge in the game of Coup,
    where a player challenges another player's Action
    '''

    REQUIRED_CARDS = {}

    def __init__(self, player1, player2):
        '''
        Constructs a challenge Response
        player1: Player representing the player who is responding
        player2: Player representing the player who made the original action
        '''
        super().__init__(player1, player2)

    @staticmethod
    def is_influence_power():
        '''
        Checks if the Challenge can be challenged
        '''
        # challenge cannot be challenged
        return False

    @staticmethod
    def cost():
        '''
        Gets the cost of the Response in coins
        '''
        return 0

    def wins_challenge(self):
        '''
        Checks if the right to make a Challenge would win a challenge
        '''
        # anyone can challenge
        return True

    @staticmethod
    def is_super():
        '''
        Checks if this Response is a super (such as Double Contessa), and
        requires a card swap either way
        '''
        return False

    def attempt_message(self):
        '''
        Gets the string representing the message for when
        the response is attempted
        '''
        return f"{self._response_by.get_user().mention} challenges {self._response_to.get_user().mention}'s claim for being a stinky horse"

    def complete_message(self):
        '''
        Gets the string representing the message for when
        the response is completed successfully
        '''
        return f"{self._response_by.get_user().mention} challenged {self._response_to.get_user().mention}'s claim for being a stinky horse"