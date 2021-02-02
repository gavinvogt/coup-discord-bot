'''
File: ambassador_block.py
Author: Gavin Vogt
This program defines the DukeBlock reponse in Coup, where
a player blocks another player's foreign aid with Duke
'''

# my code
from classes.responses import Response

class DukeBlock(Response):
    '''
    This class represents a Duke Block in the game of Coup,
    where a player uses their Duke to block another player's foreign aid
    '''

    REQUIRED_CARDS = {'duke': 1}

    def __init__(self, player1, player2):
        '''
        Constructs a duke block Response
        player1: Player representing the player who is responding
        player2: Player representing the player who made the original action
        '''
        super().__init__(self, player1, player2)

    @staticmethod
    def is_influence_power():
        '''
        Checks if the duke block can be challenged
        '''
        # duke block can be challenged
        return True

    def wins_challenge(self):
        '''
        Checks if the claimed Duke would win a challenge
        '''
        return self._response_by.has("duke")

    def attempt_message(self):
        '''
        Gets the string representing the message for when
        the response is attempted
        '''
        return f"{self._response_by.get_user().mention} attempts to block {self._response_to.get_user().mention}'s foreign aid with Duke"

    def complete_message(self):
        '''
        Gets the string representing the message for when
        the response is completed successfully
        '''
        raise f"{self._response_by.get_user().mention} blocked {self._response_to.get_user().mention}'s foreign aid with Duke"

