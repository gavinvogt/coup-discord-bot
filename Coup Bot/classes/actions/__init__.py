'''
classes.actions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A module containing the actions available
to a player in the game of Coup
'''

# Base class
from .action import Action

# Influence actions
from .steal_action import Steal
from .exchange_action import Exchange
from .assassinate_action import Assassinate
from .tax_action import Tax

# General actions
from .income_action import Income
from .foreign_aid_action import ForeignAid
from .coup_action import LaunchCoup