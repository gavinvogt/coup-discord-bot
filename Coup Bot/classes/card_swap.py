'''
File: card_swap.py
Author: Gavin Vogt
This program defines the CardSwap class, representing a swap of cards
for a player
'''

from classes.influence_card import InfluenceCard

class CardSwap:
    '''
    This class represents a card swap, where one or more card was placed
    in the draw pile, and an equal number was drawn back out

    Useful methods:
        - in_text()
        - summary_text()
    '''
    def __init__(self, swapped_in, got_back):
        '''
        Constructs a card swap, where the `placed_in` cards were swapped
        for the `drawn_out` cards
        swapped_in: list of str / InfluenceCard objects
        got_back: list of str / InfluenceCard objects
        '''
        self._to_strings(swapped_in)
        self._to_strings(got_back)
        self._in_text = self._list_to_english(swapped_in)
        self._out_text  = self._list_to_english(got_back)

    def in_text(self):
        '''
        Returns the text representing the cards that were swapped in
        '''
        return self._in_text

    def summary_text(self):
        '''
        Returns the overall summary text for the swap that occured
        '''
        return f"Swapped your {self._in_text}, for {self._out_text}"

    def _to_strings(self, cards):
        '''
        Converts the list of cards into a list of strings (in-place)
        '''
        for i in range(len(cards)):
            if isinstance(cards[i], InfluenceCard):
                cards[i] = cards[i].type.capitalize()
            else:
                cards[i] = cards[i].capitalize()

    def _list_to_english(self, cards):
        '''
        Converts a list of cards to a comma separated list of card names
        (assumes at least one card in card list)
        cards: list of cards
        Return: str, representing the cards
        '''
        num_cards = len(cards)
        if num_cards == 1:
            return f"`{cards[0]}`"
        if num_cards == 2:
            # no commas, just and
            return f"`{cards[0]}` and `{cards[1]}`"

        card_strs = []
        for i in range(num_cards):
            if i == num_cards - 1:
                # last card
                card_strs.append(f"and `{cards[i]}`")
            else:
                card_strs.append(f"`{cards[i]}`")

        return ", ".join(card_strs)