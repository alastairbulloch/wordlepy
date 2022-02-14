"""
MIT License

Copyright (c) 2022 Richard Benjamin Allen

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Acknowledgements:

Thanks to Matthew Reagan https://github.com/matthewreagan/WebstersEnglishDictionary for his JSON version of
the Guttenberg Project's Webster's Unabridged English Dictionary!
The original project can be found here: https://github.com/matthewreagan/WebstersEnglishDictionary

Thanks to Peter Coles https://github.com/mrcoles for his list of good starting words!
His interesting blog on the subject can be found here: https://mrcoles.com/best-wordle-starting-word/
"""

import argparse
import json
import os
import re
import sys

from typing import Dict, List, Optional, Pattern, Set

GOOD_STARTING_WORDS: Set = {
    "roate",
    "orate",
    "oater",
    "realo",
    "taler",
    "later",
    "ratel",
    "artel",
    "alter",
    "alert"
}


class RawPatternParseError(Exception):
    pass


class DictionaryNotFound(Exception):
    pass


class InvalidCharacterString(Exception):
    pass


class InvalidFilterCombination(Exception):
    pass


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


def _check_lists(present, absent) -> bool:
    """
    Compares two lists to see if they share common elements.  If they do this is used to reject them and prompt the
    User to correct their input.
    :param present: List of characters present in a word.
    :param absent: List of characters absent from a word.
    :return: True if the two lists share element/s; False if the lists do not share any elements.
    """
    return any(item in present for item in absent)


def _listify(chars: str) -> Optional[List]:
    """
    Converts a string into a list of characters.
    :param chars: String containing the characters you wish to turn into a list.
    :return: List of characters.
    """
    return list(chars)


def _present(word: str, p_chars: List) -> Optional[str]:
    """
    Checks a word for presence of characters from a User defined list.
    :param word: String containing the word to test against the list of characters present.
    :param p_chars: List of characters present in the word.
    :return: String containing the word if it contains the p_chars, None is it doesn't.
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
    Checks a word for absence of characters from a User defined list.
    :param word: String containing the word to test against the list of absences.
    :param a_chars: List of characters absent in the word.
    :return: String containing the word if it doesn't contain the a_chars; None if it does.
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


def __pattern_parser(raw_patten: str) -> Dict:
    """
    Parses a User defined simplified regex and turns it into a dictionary the exact length of the word, using integers
    as keys and the regex for that single character as values.  A raw_pattern such as: ?^ab^c? for example will yield
    a dictionary like {1: "[\\w]", 2: "[^a]", 3: "[b]", 4: "[^c]", 5: [\\w]}.
    :param raw_patten: String containing a simplified regex like pattern defined by the User.
    :return: Dictionary containing a regex map of the word to be guessed
    :raises RawPatternPaseException: if it finds unexpected characters in the raw_pattern.
    """
    regex_map: Dict = {}
    char_counter: int = 1

    for index, char in enumerate(raw_patten):
        if char == "?":
            regex_map[char_counter] = r"[\w]"
            char_counter += 1
        elif raw_patten[index - 1] == "^":
            regex_map[char_counter] = f"[^{char}]"
            char_counter += 1
        elif char == "^":
            continue
        elif char.isalpha():
            regex_map[char_counter] = f"[{char}]"
            char_counter += 1
        else:
            raise RawPatternParseError(f"Unexpected character encounted: {char}, please use --help or see the README "
                                       f"for the correct usage.")

    return regex_map


def _build_regex(raw_pattern: str) -> Pattern:
    """
    Uses a simplified User defined regex pattern to construct a real one, this allows a normal User to harness the
    power of Python regular expressions to be used in refining their set of words to try later.  It uses a helper
    function to construct a dictionary containing the regex for each character position.
    A dictionary like {1: "[\\w]", 2: "[^a]", 3: "[b]", 4: "[^c]", 5: [\\w]} will result in a regex pattern like
    r"^[\\w][^a][b][^c][\\w]" where the \\w is a wildcard, ^a and ^c excludes those characters in those positions
    and [b] includes the b character in that position in the word.
    :param raw_pattern: String containing a simplified regex like pattern defined by the User.
    :return: Pattern compiled in proper Python regex format.
    :raises RawPatternParseError: If the User defined raw pattern doesn't follow the accepted convention.
    """
    pattern: str = r"^"

    try:
        regex_map: Dict = __pattern_parser(raw_pattern)
    except RawPatternParseError as error:
        raise error

    for _, value in regex_map.items():
        pattern = pattern + value

    return re.compile(pattern)


def refined_by_regex(word_subset: Set, regex):
    """
    Uses regex to match words in a set against a pre-compiled regular expression pattern.
    :param word_subset: Set containing a pre-filtered words from the English dictionary.
    :param regex: Pattern containing a compiled regular expression.
    :return:  Set with reduced number of words based on the regular expression.
    """
    regex_matches: Set = set()

    for word in word_subset:
        if re.match(regex, word):
            regex_matches.add(word)

    return regex_matches


def filter_entries_by_presence_or_absence(dictionary_subset: Set, **kwargs) -> Set:
    """
    Filters a set of words further by using two helper functions that check if a list of chars is either present or
    absent from the set of words.  Uses two possible keyword arguments `present` and `absent` which contain a list of
    characters which are either present or absent from the word based on your previous wordle guesses.
    :param dictionary_subset: Set containing a pre-filtered words from the English dictionary.
    :return: Set with reduced number of words if kwargs provided; the original set of words if not.
    """
    c_present: List = kwargs.get("present")
    c_absent: List = kwargs.get("absent")

    filtered_results: Set = set()

    if not c_present and not c_absent:
        return dictionary_subset

    for word in dictionary_subset:
        if c_present and c_absent:
            if _present(word, c_present) and _absent(word, c_absent):
                filtered_results.add(word)

        elif c_present and not c_absent:
            if _present(word, c_present):
                filtered_results.add(word)

        elif c_absent and not c_present:
            if _absent(word, c_absent):
                filtered_results.add(word)

    return filtered_results


def main(worldlepy_args) -> Set:
    """
    Main function that checks the arguments passed into wordlepy and assembles a filtered set of words accordingly.
    :param worldlepy_args: Namespace containing the arguments passed via the terminal.
    :return: Set of filtered words depending on the other parameters.
    :raises ValueError: If the custom dictionary provided isn't in the correct format.
    :raises DictionaryNotFound: If the specified custom dictionary cannot be located using the path specified.
    :raises InvalidCharacterString: If the present or absent parameter string contains a non-alphabetic character.
    :raises InvalidFilterCombination: If you list a character in both present and absent parameter strings.
    """
    suggest: bool = worldlepy_args.suggest
    filtered_words: Set
    present_chars: List = []
    absent_chars: List = []

    if suggest:
        return GOOD_STARTING_WORDS

    length: int = worldlepy_args.length
    parsed_dictionary: Dict

    if not os.path.exists(worldlepy_args.dictionary):
        raise DictionaryNotFound(f"The specified path: {worldlepy_args.dictionary} doesn't exist or is invalid!")

    try:
        parsed_dictionary = parse_json("data/websters-english-dictionary.json")
    except ValueError as error:
        raise error

    if worldlepy_args.present:
        present: str = worldlepy_args.present
        if not present.isalpha():
            raise InvalidCharacterString("The present characters string you supplied contains non latin characters!")

        present_chars = _listify(worldlepy_args.present)

    if worldlepy_args.absent:
        absent: str = worldlepy_args.absent
        if not absent.isalpha():
            raise InvalidCharacterString("The absent characters string you supplied contains non latin characters!")

        absent_chars = _listify(worldlepy_args.absent)

    if _check_lists(present_chars, absent_chars):
        raise InvalidFilterCombination("Your present and absent filters cannot contain a shared element!")

    # this dictionary contains some invalid entries containing white space and other non-alphabetic characters that
    # won't ever appear in a wordle; the below will filter those out using the isalpha() conditional.
    pre_filtered_words: Set = {key for key in parsed_dictionary.keys() if len(key) == length and key.isalpha()}

    filtered_words = filter_entries_by_presence_or_absence(
        pre_filtered_words,
        present=present_chars,
        absent=absent_chars
    )

    if worldlepy_args.regex:
        for raw_regex in worldlepy_args.regex:
            regex: Pattern = _build_regex(raw_regex)
            filtered_words = refined_by_regex(filtered_words, regex)

    return filtered_words


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Terminal program to help you to optimise your wordle guesses!")

    subparser = parser.add_subparsers(dest="command")

    refine = subparser.add_parser("refine")

    parser.add_argument("-d", "--dictionary", type=str, default="data/websters-english-dictionary.json",
                        help="Specify the file path to the dictionary that you want to use, the default is "
                             "websters-english-dictionary. It has to be valid JSON in a dictionary format "
                             "i.e. it must have words as keys and the "
                             "meanings as values.")
    refine.add_argument("-p", "--present", type=str, required=False,
                        help="Specify which letters are present to help eliminate the possibilities, provide them as a "
                             "string literal e.g. `abcdefg`.")
    refine.add_argument("-a", "--absent", type=str, required=False,
                        help="Specify which letters are absent to help eliminate the possibilities, provide them as a "
                             "string literal e.g. `abcdefg`.")
    parser.add_argument("-l", "--length", type=int, required=False, default=5,
                        help="Specify the length of the word you wish to look up, the default is a length of 5 "
                             "characters.")
    refine.add_argument("-r", "--regex", type=str, action='append', required=False,
                        help="Specify a word using wild cards to eliminate some duds from the suggestions"
                             "use the following convention.")
    parser.add_argument("-s", "--suggest", action="store_true",
                        help="Use this to suggest good starting words depending on word length, default is False.")

    args = parser.parse_args()

    if args.suggest:
        if args.command == "refine":
            print("You cannot use refine when requesting suggestions for starter words!")
            sys.exit(1)

    if args.command == "refine":
        if not args.regex and not args.present and not args.absent:
            print("You cannot use refine without specifying at least one refine argument!")
            sys.exit(1)

    try:
        success = main(args)
        print(success)
    except(DictionaryNotFound, InvalidCharacterString, InvalidFilterCombination) as main_error:
        raise main_error
    except BaseException:
        raise "Unhandled exception in wordlepy"

    if success:
        sys.exit(0)
    else:
        sys.exit(1)
