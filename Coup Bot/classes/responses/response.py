'''
File: response.py
Author: Gavin Vogt
This program defines the abstract base class Response to a player's move in Coup
'''

# dependencies
import abc

class Response(metaclass=abc.ABCMeta):
    '''
    This class represents a Response in the game of Coup, performed
    as a response by one player to the Action of another

    Public fields:
        - response_by
        - response_to
        - swapped

    Methods that must be defined:
        - is_influence_power()
        - wins_challenge()
    '''
    def __init__(self, player1, player2=None):
        '''
        Constructs a general Response
        player1: Player representing the player who is responding
        player2: Player representing the player who made the original action
        '''
        self._response_by = player1
        self._response_to = player2
        self.swapped = False

    def __repr__(self):
        '''
        String representation of the Response
        '''
        return f"{self.__class__.__name__}( {repr(self._response_by)}, {repr(self._response_to)} )"

    @property
    def response_by(self):
        '''
        Gives access to the `response_by` field
        '''
        return self._response_by

    @property
    def response_to(self):
        '''
        Gives access to the `response_to` field
        '''
        return self._response_to

    @staticmethod
    @abc.abstractmethod
    def is_influence_power():
        '''
        Checks if the Response can be challenged
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def wins_challenge(self):
        '''
        Checks if the player would win a challenge
        '''
        raise NotImplementedError

    @staticmethod
    @abc.abstractmethod
    def is_super():
        '''
        Checks if this Response is a super (such as Double Contessa), and
        requires a card swap either way
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def attempt_message(self):
        '''
        Gets the string representing the message for when
        the response is attempted
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def complete_message(self):
        '''
        Gets the string representing the message for when
        the response is completed successfully
        '''
        raise NotImplementedError