'''
File: influence_card.py
Author: Gavin Vogt
This program defines the InfluenceCard class, representing
an influence card in the game of Coup
'''

class InfluenceCard:
    '''
    This class represents an influence card in a game of Coup.

    Public attributes:
        - type
        - alive
    '''
    def __init__(self, influence_type):
        '''
        Constructs a new influence card
        '''
        self._type = influence_type
        self._alive = True

    def __repr__(self):
        '''
        String representation of the card
        '''
        return f"{self.__class__.__name__}('{self._type}', alive={self._alive})"

    @property
    def type(self):
        '''
        Gives access to the `type` property
        '''
        return self._type

    @property
    def alive(self):
        '''
        Gives access to the `alive` property
        '''
        return self._alive

    @alive.setter
    def alive(self, is_alive):
        '''
        Sets the `alive` property
        '''
        self._alive = is_alive