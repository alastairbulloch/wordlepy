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
import argparse, logging, json, os, re, sys
import parse_dictionary
import wordlepy

def select_starting_word(log, dictionary_path, length, word_id):
    # get the parsed dictionary
    parsed_dict = parse_dictionary.parse(dictionary_path, length)
    
    # yuk! sets aren't indexable
    reference_word = None
    for id, word in enumerate(sorted(parsed_dict)):
        if id == word_id:
            reference_word = word
            break
            
    log.info("Reference word (id=%d): '%s'" % (word_id, reference_word))
    
    return reference_word
    
       
    

def logging_define_verbosity( logger, cmdline_verbose, cmdline_quiet ):
    """ Change the logging level depending on the verbosity input value from the command line """
    
    argparse_verb_mult = 10    # argparse verbosity multipler
     
    verbosity = logging.INFO / argparse_verb_mult    # rebase to count v and q arguments more easily
    
    # strange, more verbose is lower number and more verbose is higher
    verbosity -=  cmdline_verbose
    verbosity +=  cmdline_quiet  
    
    assert verbosity >= 0 and verbosity <= 4, "Unexpected verbosity level: %d. Check quiet and verbose arguments" % verbosity
    
    verbosity  = verbosity * argparse_verb_mult    # rebase to logging module values again
    
    logger.setLevel(int(verbosity))
    
    logger.debug("Logging verbosity: %d" % verbosity)

def commandline_interface( log, argv ):
    
    #default output file name
    #default_output_file_pfx = __file__.replace(".py","") +"_output"
    
    # Argument parser
    parser = argparse.ArgumentParser( description='Test the wordle solution algorithm',
                                     # display defaults
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    # Placement arguments
    # None at the moment
            
    # Optional arguments
    parser.add_argument("-d", "--dictionary", type=str, default="data/websters-english-dictionary.json",
                        help="Specify the file path to the dictionary that you want to use, the default is "
                             "websters-english-dictionary. It has to be valid JSON in a dictionary format "
                             "i.e. it must have words as keys and the "
                             "meanings as values.")
    parser.add_argument("-l", "--length", type=int, required=False, default=5,
                        help="Specify the length of the word you wish to look up, the default is a length of 5 "
                             "characters.")
                             
                             
    parser.add_argument("-i", "--word-id", type=int, required=False, default=0,
                        help="Specify the dictionary word id to use as a reference. -1 signifies all words (i.e. regression mode)")
    
    parser.add_argument('--verbose', '-v',     action='count', default=0,
                        help="Increment verbosity level by one" )
    parser.add_argument('--quiet',      '-q',     action='count', default=0,
                        help="Decrement verbosity level by one", )
    
    args = parser.parse_args(argv)
    
    return args


def define_logger():
    # Prefix all logs with timestamps
    logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
    log = logging.getLogger(__name__)
    log.setLevel(logging.INFO)
    
    # Configure console output
    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setFormatter(logFormatter)
    log.addHandler(consoleHandler) 	
    
    return log

def main(argv):
    log = define_logger()
    
    args = commandline_interface(log, argv)
    
    logging_define_verbosity(log, args.verbose, args.quiet)
    
    
    if args.word_id != -1:
        word_ids = [args.word_id]
    else:
        word_ids = 100000000000000 # i'm lazy, how big is the dictionary?
    
    # main test loop   
    for word_id in word_ids:
        reference_word = select_starting_word(log, args.dictionary, args.length, args.word_id)
        reference_letters = list(reference_word)

        # solution loop
        
        # initial starting guess
        suggested_words = wordlepy.main(["--suggest"])
        guess_word = suggested_words[0]
        guess_letters = list(guess_word)

        log.debug("Starting word: '%s'" % guess_word)

        # Store the letters found
        correct_positions = ['?','?','?','?','?'] # TODO: allow this to handle any word size
        correct_letters = ""
        incorrect_letters = ""

        solution_counter = 0
        while True: # don't impose a limit like real wordle does
            
            solution_counter = solution_counter + 1 # increment our number of tries counter

            # perform comparison
            if guess_word == reference_word:
                log.info("Solved in %d attempt(s)" % solution_counter)
                break
            
            # perform letter comparison
            for id, letter in enumerate(guess_letters):

                # check letter is within the word
                if (letter in reference_letters):
                    if (letter not in correct_letters):
                        correct_letters = correct_letters + letter
                    else:
                        pass # No need to dupliate the list
                elif letter not in incorrect_letters: # No need to dupliate the list
                    incorrect_letters = incorrect_letters + letter

                # check positionality: use a simplified approach where we don't exclude letters from specific positions, just in totol
                # TODO: implement the exclusion of included letters from specific positions.
                if guess_letters[id] == reference_letters[id]:
                    correct_positions[id] = reference_letters[id]

            search_exp = "".join(correct_positions)
                 
            log.debug("Correct letters: '%s', Incorrect letters: '%s', Search pattern: '%s'" % (correct_letters, incorrect_letters, search_exp) )
                        
            # get next guess word whilst refining
            guess_words = wordlepy.main(["refine", "-p", correct_letters, "-a", incorrect_letters,  "-r","%s" % search_exp])
            guess_word = guess_words[0]
            guess_letters = list(guess_word)

            log.debug("Guess word: '%s'" % guess_word)
            
            
            
            
        
    
    
    
    

if __name__ == "__main__":
    main(sys.argv[1:])