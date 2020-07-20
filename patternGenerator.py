import argparse
import json
import sys
from collections import defaultdict
import Analyzier

pattern = dict()


def load_pattern():
    """
    This method loads the saved settings (mapping rules) from ``settings.json``.

    :return: void.
    """
    global pattern
    try:
        # open the settings.json file and store mapping rules in settings dict
        with open('pattern.json') as pattern_file:
            pattern = json.load(pattern_file)
            print('Successful!\n')
            return pattern

    except IOError:  # handles IO errors
        print("pattern files doesn't exist!!! ")
        sys.exit(1)


def show_pattern(settings):
    global pattern
    """
    Shows existing classes and related mappings and displays all the mapping rules.

    :param settings: the existing settings dict, containing mapping rules.

    :return: void.
    """
    mappings = pattern["PATTERN"]  # load the default mapping rules
    print('Following are the pattern and its number:')

    # prints all the existing mapping rules
    for key in mappings.keys():
        print('   ' + key + ':' + mappings[key])


def dump_pattern(pattern_json):
    global pattern

    pattern_file = open("pattern.json", "w+")
    pattern_file.write(json.dumps(pattern_json))  # saves/updates the existing settings
    pattern_file.close()
    print("pattern reload!")
    pattern = load_pattern()  # reload the saved settings into the memory

    return


def add_pattern():

    global pattern
    pattern_string = defaultdict(dict)

    pattern_string = input('Enter the pattern: ').strip()

    print(json.dumps(pattern_string, indent=4))

    save_pattern = input("\nDo you want to save this Mapper Function? (Y/N): ")
    if save_pattern in ['y', 'Y', 'yes', 'Yes']:
        # dump the existing dictionary into `custom_mappers.json` and save mapper function permanently
        pattern['PATTERN'][len(pattern["PATTERN"]) + 1] = pattern_string
        dump_pattern(pattern)
        print('pattern saved!!')
        return
    else:
        print('Aborted!!!')
        return


def main():
    """
    Entry point for patternGenerator.
    Parses parameters and calls other modules in order to create/modify ``pattern.json`` file.

    :return: void
    """

    # initialize argparse parameters
    parser = argparse.ArgumentParser(description=' Add/Replace pattern in pattern.json for different patterns'
                                                 '\n that can be used by list-extractor.',
                                     formatter_class=argparse.RawTextHelpFormatter,
                                     usage="patternGenerator.py [--help] collection_mode resource language "
                                           "\nUse patternGenerator.py -h for more details.\n ")
    print('Loading pattern file....')

    # initialize the dictionaries with the saved settings
    settings = load_pattern()  # initializes mapping rules

    # the prompt message
    prompt_str = "Select one of the following options:\n\n" \
                 "1. Show existing pattern\n" \
                 "2. Add new pattern\n" \
                 "3. Analyer mod\n" \
                 "0. Quit\n" \
                 "\nYour option: "
    print('')

    # option parser; decides the flow of the program according to what user wants to do.
    while True:
        try:
            # display and accept actions for different options
            run = int(input(prompt_str))
            if run == 1:
                show_pattern(settings)
            elif run == 2:
                add_pattern()
            elif run == 3:
                Analyzier.group_process()
            elif run == 0:
                sys.exit(0)
            else:
                print('Invalid option! \n')
                continue
            input()
        # if user gives any other input, loop the prompt.
        except SyntaxError:
            print('Invalid option! \n')


if __name__ == "__main__":
    main()
