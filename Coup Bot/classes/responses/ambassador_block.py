'''
File: ambassador_block.py
Author: Gavin Vogt
This program defines the AmbassadorBlock reponse in Coup, where
a player blocks another player's steal attempt with Ambassador
'''

# my code
from classes.responses import Response

class AmbassadorBlock(Response):
    '''
    This class represents an Ambassador Block in the game of Coup,
    where a player uses their Ambassador to block another player's steal
    '''

    REQUIRED_CARDS = {'ambassador': 1}

    def __init__(self, player1, player2):
        '''
        Constructs an ambassador block Response
        player1: Player representing the player who is responding
        player2: Player representing the player who made the original action
        '''
        super().__init__(self, player1, player2)

    @staticmethod
    def is_influence_power():
        '''
        Checks if the ambassador block can be challenged
        '''
        # ambassador block can be challenged
        return True

    def wins_challenge(self):
        '''
        Checks if the claimed Ambassador would win a challenge
        '''
        return self._response_by.has("ambassador")

    def attempt_message(self):
        '''
        Gets the string representing the message for when
        the response is attempted
        '''
        return f"{self._response_by.get_user().mention} attempts to block {self._response_to.get_user().mention}'s steal with Ambassador"

    def complete_message(self):
        '''
        Gets the string representing the message for when
        the response is completed successfully
        '''
        raise f"{self._response_by.get_user().mention} blocked {self._response_to.get_user().mention}'s steal with Ambassador"

