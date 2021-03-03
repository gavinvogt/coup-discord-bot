'''
File: action.py
Author: Gavin Vogt
This program defines the abstract base class Action for a player's move in Coup
'''

# dependencies
from discord import Embed, Color
import abc

class Action(metaclass=abc.ABCMeta):
    '''
    This class represents an Action in the game of Coup, performed
    by a player (possibly to another player).

    Public properties:
        - done_by
        - done_to
        - swapped

    Methods that must be defined:
        - attempt_message()
        - complete_message()
        - is_influence_power()
        - is_blockable()
        - requires_response()
        - cost()
        - wins_challenge()
        - perform_action()
        - undo_action()
        - available_responses(channel_mention)
    '''
    def __init__(self, player1, player2=None):
        '''
        Constructs a general Action
        player1: Player representing the player who performed the action
        player2: Player representing the player who the action was done to (optional)
        '''
        self._done_by = player1
        self._done_to = player2
        self.swapped = False

    def __repr__(self):
        '''
        String representation of the Action
        '''
        return f"{self.__class__.__name__}( {repr(self._done_by)}, {repr(self._done_to)} )"

    @property
    def done_by(self):
        '''
        Gives access to the `done_by` property
        Type: Player
        '''
        return self._done_by

    @property
    def done_to(self):
        '''
        Gives access to the `done_to` property
        Type: Player or None
        '''
        return self._done_to

    @staticmethod
    @abc.abstractmethod
    def is_influence_power():
        '''
        Checks if this Action requires a certain influence (in which
        case it could be challenged)
        '''
        raise NotImplementedError

    @staticmethod
    @abc.abstractmethod
    def is_blockable():
        '''
        Checks if this Action can be blocked by another player
        '''
        raise NotImplementedError

    @staticmethod
    @abc.abstractmethod
    def requires_response():
        '''
        Checks if a Response is required for gameplay to continue,
        whether the response comes as a Challenge or a Pass
        '''
        raise NotImplementedError

    @staticmethod
    @abc.abstractmethod
    def can_block_with(influence):
        '''
        Checks if the given influence card can block this Action
        '''
        raise NotImplementedError

    @staticmethod
    @abc.abstractmethod
    def cost():
        '''
        Gets the cost of the Action in coins
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def wins_challenge(self):
        '''
        Checks if the player wins the challenge
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def perform_action(self):
        '''
        Performs an action to the player(s)
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def undo_action(self):
        '''
        Undoes the action to the player(s)
        '''
        raise NotImplementedError

    @staticmethod
    @abc.abstractmethod
    def is_super():
        '''
        Checks if this Action is a super (such as Double Contessa), and
        requires a card swap either way
        '''
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def available_responses(cls, channel_mention):
        '''
        Returns the embed holding available responses to
        an action
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def attempt_message(self):
        '''
        Gets the string representing the message for when
        the action is attempted
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def complete_message(self):
        '''
        Gets the string representing the message for when
        the action is completed successfully
        '''
        raise NotImplementedError

    @staticmethod
    def response_embed(responses, channel_mention):
        '''
        Generates an embed of available responses from the given list
        responses: list of names of available responses to the action
        channel_mention: str, representing the @mention for the channel
        the game is occurring in
        '''
        embed = Embed(
            title = "Available Responses",
            description = "``` - " + "\n - ".join(responses) + "```",
            color = Color.red(),
        )
        embed.add_field(name="Channel", value=channel_mention)
        return embed