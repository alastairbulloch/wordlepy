import json
import re

from typing import Dict, List, Optional, Pattern, Set


class PatternLengthException(Exception):
    pass


def parse_json(file_path: str) -> Dict:
    """

    :param file_path:
    :return:
    """
    english_dictionary: Dict = {}

    with open(file_path, "r") as file:
        try:
            english_dictionary = json.load(file)
        except ValueError as error:
            raise error

    return english_dictionary


def _present(word: str, p_chars: List) -> Optional[str]:
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
    matches: List = []

    for char in a_chars:
        if char not in word:
            matches.append(True)
        else:
            matches.append(False)

    if all(matches):
        return word

    return None


def _build_regex(raw_pattern: str, length: int = 5, present: bool = True) -> Pattern:
    if len(raw_pattern) > length:
        raise PatternLengthException("Raw pattern used is greater than the set length.")

    pattern: str = r"^"

    if not raw_pattern:
        return re.compile(r"^[\w][\w][\w][\w][\w]")

    for char in raw_pattern:
        if char == "?":
            pattern = pattern + "[\w]"
        if present and char.isalpha():
            pattern = pattern + f"[{char}]"
        if not present and char.isalpha():
            pattern = pattern + f"[^{char}]"

    regex = re.compile(pattern)
    return regex


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


def main():
    raw_dictionary: Dict = parse_json("/home/richard/git/wordlepy/data/websters-english-dictionary.json")

    words_with_five_letters: Set = {key for key in raw_dictionary.keys() if len(key) == 5 and " " not in key}

    filtered_words: Set = filter_entries(words_with_five_letters, present=["n", "k", "l"], absent=["f", "u", "d", "r", "a", "i", "e", "c", "s"])

    print(filtered_words)


if __name__ == "__main__":
    main()
