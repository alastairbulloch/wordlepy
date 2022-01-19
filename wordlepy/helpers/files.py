import json

from typing import Dict, Set


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


def filter_entries(dictionary_subset: Set, **kwargs) -> Set:
    """

    :param dictionary_subset:
    :param kwargs:
    :return:
    """
    # example kwargs could be: contains, exclude, pattern_match, length, good_starters
    # research some good starter patterns, like least number of guesses that eliminate most words?
    pass


def main():
    raw_dictionary: Dict = parse_json("/home/richard/git/wordlepy/data/websters-english-dictionary.json")

    words_with_five_letters: Set = {key for key in raw_dictionary.keys() if len(key) == 5 and " " not in key}

    print(words_with_five_letters)


if __name__ == "__main__":
    main()
