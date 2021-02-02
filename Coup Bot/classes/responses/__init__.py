'''
classes.responses
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A module containing the responses available
to a player in the game of Coup
'''

# Base class
from .response import Response

# Influence actions
from .contessa_block import ContessaBlock
from .captain_block import CaptainBlock
from .ambassador_block import AmbassadorBlock
from .duke_block import DukeBlock
from .double_contessa_block import DoubleContessaBlock

# General actions
from .challenge import Challenge
from .pass_response import Pass
from .die_response import Die