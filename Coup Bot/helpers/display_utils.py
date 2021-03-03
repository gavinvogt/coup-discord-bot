'''
File: display_utils.py
Author: Gavin Vogt
This program provides helpful functions for displaying items
'''

def ordered_list(items):
    '''
    Returns a string representing the ordered list of the given item
    items: list of items to put in ordered list
    '''
    return "\n".join(f"{num}. {item}" for num, item in enumerate(items, 1))