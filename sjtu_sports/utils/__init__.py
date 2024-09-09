from random import choice
from time import time


table = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", 
         "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", 
         "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", 
         "U", "V", "W", "X", "Y", "Z"]

def get_key():
    key = ""
    for i in range(16):
        key += choice(table)
    return key


def get_timestamp_ms():
    """
    Get current unix timestamp in milliseconds.
    
    Returns:
        int: current unix timestamp in milliseconds.
    """
    return str(int(time() * 1000))