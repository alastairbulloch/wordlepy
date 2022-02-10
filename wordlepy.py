import argparse
import json
import re
import sys

from typing import Dict, List, Optional, Pattern, Set


class PatternLengthException(Exception):
    pass


def parse_json(file_path: str) -> Dict:
    """

    :param file_path: String
    :return: Dictionary containing key value pairs of the JSON file
    :raises: ValueError if the function cannot load the JSON file
    """
    english_dictionary: Dict = {}

    with open(file_path, "r") as file:
        try:
            english_dictionary = json.load(file)
        except ValueError as error:
            raise error

    return english_dictionary


def __listify(chars: str) -> Optional[List]:
    """

    :param chars: String containing the characters you wish to turn into a list
    :return: List of characters or None if chars are invalid
    """
    pass

def _present(word: str, p_chars: List) -> Optional[str]:
    """

    :param word: String
    :param p_chars: List
    :return: String containing the word if it contains the p_chars, None is it doesn't
    """
    matches: List = []

    for char in p_chars:
        if char in word:
            matches.append(True)
        else:
            matches.append(False)

    if all(matches):
        return word

    return None


def _absent(word: str, a_chars: List) -> Optional[str]:
    """

    :param word: String
    :param p_chars: List
    :return: String containing the word if it doesn't contain the p_chars, None is it does
    """
    matches: List = []

    for char in a_chars:
        if char not in word:
            matches.append(True)
        else:
            matches.append(False)

    if all(matches):
        return word

    return None


def _build_regex(raw_pattern: str, length: int, present: bool = True) -> Pattern:
    """

    :param raw_pattern: String
    :param length: Int
    :param present: Boolean
    :return: Regex pattern
    """
    if len(raw_pattern) > length:
        raise PatternLengthException(
            "Raw pattern used is greater than the set length.")

    pattern: str = r"^"

    if not raw_pattern:
        pattern = r"^[\w][\w][\w][\w][\w]"

    # todo: add a convention to the string input that indicates present or absent e.g. ^fb^c^de where a preceding
    #  ^ means the letter is abscent from that position but present in the word

    for char in raw_pattern:
        if char == "?":
            pattern = pattern + "[\w]"
        if present and char.isalpha():
            pattern = pattern + f"[{char}]"
        if not present and char.isalpha():
            pattern = pattern + f"[^{char}]"

    return re.compile(pattern)


def exclude_positions() -> Optional[str]:
    pass


def include_positions() -> Optional[str]:
    pass


def filter_entries(dictionary_subset: Set, **kwargs) -> Set:
    """

    :param dictionary_subset:
    :param kwargs:
    :return:
    """
    c_present: List = kwargs.get("present")
    c_absent: List = kwargs.get("absent")
    # length: int = kwargs.get("length") or 5

    filtered_results: Set = set()

    for word in dictionary_subset:
        if _present(word, c_present) and _absent(word, c_absent):
            filtered_results.add(word)

    # example kwargs could be: contains, exclude, pattern_match, length, good_starters
    # research some good starter patterns, like least number of guesses that eliminate most words?
    return filtered_results


def main(worldlepy_args) -> Set:
    raw_dictionary: Dict = parse_json("data/websters-english-dictionary.json")

    words_with_five_letters: Set = {key for key in raw_dictionary.keys() if len(key) == 5 and " " not in key}

    filtered_words: Set = filter_entries(words_with_five_letters,
        present=["a", "w", "c", "k"],
        absent=["r", "s", "t", "e", "d", "m", "i", "l", "y"])

    return filtered_words


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description= "Terminal program to help you to optimise your wordle guesses!")

    subparser = parser.add_subparsers(dest="command")

    refine = subparser.add_parser("refine")

    parser.add_argument("-d", "--dictionary", type=str, default="data/websters-english-dictionary.json",
                        help="Specify the dictionary that you want to use, the default is websters-english-dictionary. "
                             "It has to be valid JSON in a dictionary format i.e. it must have words as keys and the "
                             "meanings as values.")
    refine.add_argument("-p", "--present", type=str, required=False,
                        help="Specify which letters are present to help eliminate the possibilities, provide them as a "
                             "string literal e.g. `abcdefg`")
    refine.add_argument("-a", "--absent", type=str, required=False,
                        help="Specify which letters are absent to help eliminate the possibilities, provide them as a "
                             "string literal e.g. `abcdefg`")
    parser.add_argument("-l", "--length", type=int, required=False, default=5,
                        help="Specify the length of the word you wish to look up, the default is a length of 5 "
                             "characters")
    refine.add_argument("-r", "--regex", type=str, required=False,
                        help="Specify a word using wild cards to eliminate some duds from the suggestions"
                             "use the following convention")
    parser.add_argument("-s", "--suggest", type=bool, action="store_true",
                        help="Use this to suggest good starting words depending on word length, default is False")

    args = parser.parse_args()

    # only allow suggest if suggest is used
    # if regex is used then present or absent needs to be used

    try:
        success = main(args)
    except BaseException as error:
        raise "Unhandled exception in wordlepy"

    if success:
        sys.exit(0)
    else:
        sys.exit(1)
