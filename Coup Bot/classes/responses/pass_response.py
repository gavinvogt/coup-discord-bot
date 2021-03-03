'''
File: pass_response.py
Author: Gavin Vogt
This program defines the Pass reponse in Coup, where
a player passes on responding to another's Action / Response
'''

# my code
from classes.responses import Response

class Pass(Response):
    '''
    This class represents a Pass in the game of Coup,
    where a player passes on responding to another
    '''

    REQUIRED_CARDS = {}

    def __init__(self, player1, player2):
        '''
        Constructs a pass Response
        player1: Player representing the player who is passing
        player2: Player representing the player who made the original action
        '''
        super().__init__(player1, player2)

    @staticmethod
    def is_influence_power():
        '''
        Checks if the pass can be challenged
        '''
        return False

    def wins_challenge(self):
        '''
        Checks if the pass would win a challenge
        '''
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
        return f"{self._response_by.get_user().mention} passes on responding to {self._response_to.get_user().mention}'s action"

    def complete_message(self):
        '''
        Gets the string representing the message for when
        the response is completed successfully
        '''
        raise f"{self._response_by.get_user().mention} passed on responding to {self._response_to.get_user().mention}'s action"