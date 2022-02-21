"""
Load the local dictionary and perform any culling of words that can't be used etc.
"""

import json
from typing import Dict, List, Optional, Pattern, Set

def parse_json(file_path: str) -> Dict:
    """
    Parses a JSON file into a Python dictionary for use in creating filtered subsets.
    :param file_path: String containing the file path to the dictionary you wish to parse.
    :return: Dictionary containing key value pairs of the JSON file.
    :raises: ValueError if the function cannot load the JSON file.
    """
    english_dictionary: Dict = {}

    with open(file_path, "r") as file:
        try:
            english_dictionary = json.load(file)
        except ValueError:
            raise ValueError("Could not parse dictionary, it is probably not in the right format!")

    return english_dictionary
    
    
   
    

def parse(path, length):
    """
    Parse the defined dictionary JSON file and return the parsed state
    """
    
    try:
        parsed_dictionary = parse_json(path)
    except ValueError as error:
        raise error
                
    # this dictionary contains some invalid entries containing white space and other non-alphabetic characters that
    # won't ever appear in a wordle; the below will filter those out using the isalpha() conditional.
    pre_filtered_words: Dict = {key for key in parsed_dictionary.keys() if len(key) == length and key.isalpha()}
        
    return pre_filtered_words

