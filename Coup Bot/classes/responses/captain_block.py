'''
File: captain_block.py
Author: Gavin Vogt
This program defines the CaptainBlock reponse in Coup, where
a player blocks another player's steal attempt with Captain
'''

# my code
from classes.responses import Response

class CaptainBlock(Response):
    '''
    This class represents a Captain Block in the game of Coup,
    where a player uses their Captain to block another player's steal
    '''

    REQUIRED_CARDS = {'captain': 1}

    def __init__(self, player1, player2):
        '''
        Constructs a captain block Response
        player1: Player representing the player who is responding
        player2: Player representing the player who made the original action
        '''
        super().__init__(self, player1, player2)

    @staticmethod
    def is_influence_power():
        '''
        Checks if the captain block can be challenged
        '''
        # captain block can be challenged
        return True

    def wins_challenge(self):
        '''
        Checks if the claimed Captain would win a challenge
        '''
        return self._response_by.has("captain")

    def attempt_message(self):
        '''
        Gets the string representing the message for when
        the response is attempted
        '''
        return f"{self._response_by.get_user().mention} attempts to block {self._response_to.get_user().mention}'s steal with Captain"

    def complete_message(self):
        '''
        Gets the string representing the message for when
        the response is completed successfully
        '''
        raise f"{self._response_by.get_user().mention} blocked {self._response_to.get_user().mention}'s steal with Captain"


