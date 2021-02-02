'''
File: double_contessa_block.py
Author: Gavin Vogt
This program defines the DoubleContessaBlock reponse in Coup, where
a player blocks another player's coup attempt with Double Contessa
'''

# my code
from classes.responses import Response

class DoubleContessaBlock(Response):
    '''
    This class represents a Contessa Block in the game of Coup,
    where a player used their two contessas to block a coup
    '''

    REQUIRED_CARDS = {'contessa': 2}

    def __init__(self, player1, player2):
        '''
        Constructs a double contessa block Response
        player1: Player representing the player who is responding
        player2: Player representing the player who made the original action
        '''
        super().__init__(self, player1, player2)

    @staticmethod
    def is_influence_power():
        '''
        Checks if the double contessa block can be challenged
        '''
        # double contessa block can be challenged
        return True

    def wins_challenge(self):
        '''
        Checks if the claimed Double Contessa would win a challenge
        '''
        return self._response_by.has("contessa", 2)

    def attempt_message(self):
        '''
        Gets the string representing the message for when
        the response is attempted
        '''
        return f"{self._response_by.get_user().mention} attempts to block {self._response_to.get_user().mention}'s coup with Double Contesssa"

    def complete_message(self):
        '''
        Gets the string representing the message for when
        the response is completed successfully
        '''
        raise f"{self._response_by.get_user().mention} blocked {self._response_to.get_user().mention}'s coup with Double Contesssa"

