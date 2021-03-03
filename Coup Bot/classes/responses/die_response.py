'''
File: die_response.py
Author: Gavin Vogt
This program defines the Die class, which represents
choosing a card to die in Coup
'''

# my code
from classes.responses import Response

class Die(Response):
    '''
    This class represents a death in the game of Coup,
    where a player chooses which influence of theirs to die
    '''

    REQUIRED_CARDS = {}

    def __init__(self, player, *indexes_to_kill):
        '''
        Constructs a die Response
        player: Player representing the player who is killing a card
        indexes_to_kill: list of ints, representing the indexes of the player's
        influence card to kill (indexed starting at 0)
        '''
        super().__init__(player)
        self._indexes = indexes_to_kill

    @staticmethod
    def is_influence_power():
        '''
        Checks if the death can be challenged
        '''
        return False

    def wins_challenge(self):
        '''
        Checks if the death would win a challenge
        '''
        return True

    def perform_action(self):
        '''
        Performs the action of the Response
        '''
        # kill the cards
        for index in self._indexes:
            self._response_by[index].alive = False

        # change the number of cards the player needs to kill
        self._response_by.must_kill -= len(self._indexes)

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
        types = [ self._response_by[i].type.capitalize() for i in self._indexes ]
        return f"{self._response_by.get_user().mention} let their `{'`, `'.join(types)}` die"

    def complete_message(self):
        '''
        Gets the string representing the message for when
        the response is completed successfully
        '''
        return self.attempt_message()