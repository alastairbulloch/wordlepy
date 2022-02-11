# Wordlepy

## Introduction
A simple Python 3.9 terminal program to help in the winning of wordles!  The implementation is an automation of the
general strategy that I have been using to guess the daily wordles.  

1. Use a good starting word with high entropy.
1. Eliminate words that contain certain characters
2. Include words that contain certain characters
3. Eliminate words based on what we know about the locations of characters e.g. where they do and do not occur

You can swap the dictionary used for another language if it's in the same format (JSON) as the default used in this 
project i.e. the Webster's Unabridged English Dictionary.  As long as it is recognised by the Python method `isalpha`.

## Installation
This project requires Python 3.9 installing or a virtual environment that uses Python 3.9.  It uses the native modules 
found in this version of Python and therefore does not have any other dependencies.

## Basic Usage
Because the project uses argparser, you can get help by using the following command from a terminal:

```bash
python wordlepy.py --help
```

To suggest a set of starting words based on the research of Peter Coles use the following command:

```bash
python wordle.py -s
```

To include a list of characters present in the word based on previous guesses use the following command:

```bash
python wordle.py refine -p "abc"
```

To exclude a list of characters absent in the word based on previous guesses use the following command:

```bash
python wordle.py refine -a "def"
```

To include and exclude lists of characters in a word based on previous guesses use the following command:

```bash
python wordle.py refine -p "abc" -a "def"
```

To use regex and exlusion/inclusion lists based on previous guesses use the following command:

```bash
python wordle.py refine -p "abc" -a "def" -r "?ab^c?"
```
**N.B.** Use ? to specify a wild card, preceed a character that is present but not in that location with a ^ (yellow)
and simply list a character in that position in the word (green).

To change the default dictionary use the following argument in the command, where path_to_alternative_dictionary is the 
exact file path to the dictionary you wish to use instead:

```bash
python wordle.py -d "path_to_alternative_dictionary"
```

To change the default length (the default is 5) of the word use the following argument in the command:

```bash
python wordle.py -l 6
```

You can use many combinations of arguments with each other, for example:

```bash
python wordle.py -l 6 -d "path_to_alternative_dictionary" refine -p "abc" -a "def" -r "?a^b^c?"
```

## Acknowledgements
Thanks to Matthew Reagan https://github.com/matthewreagan/WebstersEnglishDictionary for his JSON version of
the Guttenberg Project's Webster's Unabridged English Dictionary! 
The original project can be found here: https://github.com/matthewreagan/WebstersEnglishDictionary

Thanks to Peter Coles https://github.com/mrcoles for his list of good starting words!
His interesting blog on the subject can be found here: https://mrcoles.com/best-wordle-starting-word/
