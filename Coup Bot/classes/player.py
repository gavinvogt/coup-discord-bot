'''
File: player.py
Author: Gavin Vogt
This program defines a Coup player
'''

# dependencies
from discord import Embed, Color
from datetime import datetime

# my code
from classes.influence_card import InfluenceCard


class Player:
    '''
    This class represents a player in a game of Coup.

    Public attributes:
        - must_kill
        - must_swap

    Useful methods:
        - get_id()
        - get_user()
        - get_mention()
        - get_coins()
        - add_coins(num_coins)
        - has(influence_type, count)
        - must_coup()
        - get_embed(ctx)
        - is_eliminated()
    '''

    MUST_COUP_COINS = 10

    def __init__(self, user, start_coins, num_influences):
        '''
        Constructs a new coup player
        user: discord.User object for the player
        start_coins: number of coins the player starts with
        num_influences: number of influence cards the player starts with
        '''
        # Information about the player's state
        self._user = user
        self._coins = start_coins
        self._influences = [None for _ in range(num_influences)]

        # Required actions from the player before turn can complete
        self._must_kill = 0
        self._must_swap = False

    def __repr__(self):
        '''
        String representation of the Player
        '''
        return f"Player({self._user}, coins={self._coins}, lives={self.life_count()})"

    def __getitem__(self, index):
        '''
        Gets the influence card at the given index
        index: int, representing the index of the influence card
        '''
        return self._influences[index]

    @property
    def must_kill(self):
        '''
        Access to the `must_kill` property, which tracks how many
        of their own cards the player is required to kill before
        the game can continue.

        If are technically required to kill more than the number of
        lives they have, returns the number of lives instead
        '''
        return min(self._must_kill, self.life_count())

    @must_kill.setter
    def must_kill(self, num_to_kill):
        '''
        Sets the number of cards the player must kill
        '''
        self._must_kill = num_to_kill

    @property
    def must_swap(self):
        '''
        Get whether the player must make a swap before the game
        can continue (FOR EXCHANGES)
        '''
        return self._must_swap

    @must_swap.setter
    def must_swap(self, num_to_swap):
        '''
        Setter for the `must_swap` property
        '''
        self._must_swap = num_to_swap

    def get_id(self):
        '''
        Getter for the user ID
        '''
        return self._user.id

    def get_user(self):
        '''
        Getter for the player's discord.User object
        '''
        return self._user

    def get_mention(self):
        '''
        Getter for the player's @mention
        '''
        return self._user.mention

    def get_coins(self):
        '''
        Gets the number of coins the player has
        '''
        return self._coins

    def set_coins(self, num_coins):
        '''
        Sets the number of coins the player has
        num_coins: int, representing the player's new coins
        '''
        self._coins = num_coins

    def add_coins(self, num_coins):
        '''
        Adds a certain number of coins to the player
        num_coins: int, representing how many coins to add
        '''
        self._coins += num_coins

    def get_count(self, influence_type):
        '''
        Gets this player's count of the given influence card
        influence_type: str, representing the influence type to count
        '''
        count = 0
        influence_type = influence_type.lower()
        for influence in self._influences:
            if influence is not None and influence.alive and influence.type == influence_type:
                count += 1
        return count

    def has(self, influence_type, count=1):
        '''
        Checks if this player has the given count of the given card
        influence_type: str, representing the card type
        count: int, representing the minimum number of the card the
        player must have
        Return: True if the player has >= count, False otherwise
        '''
        return (self.get_count(influence_type) >= count)

    def must_coup(self):
        '''
        Checks if the player is required to make a coup on this turn
        '''
        return (self._coins >= self.MUST_COUP_COINS)

    def get_influences(self):
        '''
        Gets the list of influence cards the player has
        '''
        return self._influences

    def set_influence(self, index, influence_type):
        '''
        Sets one of the Player's influence cards to be the
        given influence types
        index: int, representing the slot to place the influence card at
        influence_type: str, representing the influence card type
        '''
        self._influences[index] = InfluenceCard(influence_type.lower())

    def get_embed(self, ctx):
        '''
        Generates the discord embed representing the Player
        ctx: discord Context object
        '''
        player_embed = self._get_basic_embed(show_influences=True)
        player_embed.title = "Your Hand"
        player_embed.add_field(name="Server", value=ctx.guild.name)
        player_embed.add_field(name="Channel", value=ctx.channel.mention)
        return player_embed

    def get_visible_embed(self):
        '''
        Generates the discord embed representing the Player, but
        with only the information visible to other Players
        '''
        player_embed = self._get_basic_embed(show_influences=False)
        player_embed.title = "Player Hand"
        return player_embed

    def life_count(self):
        '''
        Gets the player's life count
        '''
        count = 0
        for influence in self._influences:
            if influence.alive:
                count += 1
        return count

    def is_eliminated(self):
        '''
        Checks if the player is eliminated from the game
        '''
        return not (self.life_count() > 0)

    def _get_basic_embed(self, show_influences):
        # Set up the embed
        player_embed = Embed(
            color = Color.orange(),
            timestamp = datetime.utcnow(),
        )

        # Keep track of all the player's influences
        influences = []
        for i in range(len(self._influences)):
            influence = self._influences[i]
            if influence is not None:
                if influence.alive:
                    # influence card is alive
                    if show_influences:
                        influences.append(f"{influence.type.capitalize()}")
                    else:
                        influences.append("[HIDDEN]")
                else:
                    # influence card is dead (revealed)
                    influences.append(f"~~{influence.type.capitalize()}~~")
                i += 1
        indices = [str(i + 1) for i in range(len(self._influences))]
        player_embed.add_field(name="⭐", value="\n".join(indices))
        player_embed.add_field(name="Influences", value="\n".join(influences))
        player_embed.add_field(name="Coins 🪙", value=self._coins)
        player_embed.set_thumbnail(url=self._user.avatar_url)
        player_embed.set_footer(text="Requested at")
        return player_embed