import json
import re
import sys

pattern_string = dict()
pattern_symbol = list()


def load_json():
    """
        This method loads the saved settings (mapping rules) from ``settings.json``.

        :return: void.
        """
    global pattern_string
    try:
        # open the settings.json file and store mapping rules in settings dict
        with open('pattern.json') as pattern_file:
            pattern_string = json.load(pattern_file)
            print('Successful!\n')
            return pattern_string

    except IOError:  # handles IO errors
        print("pattern files doesn't exist!!! ")
        sys.exit(1)


def group_process():
    load_json()
    for key in pattern_string['PATTERN']:
        print("analyzer " + key + "from :" + pattern_string['PATTERN'][key])
        string_analyzier(pattern_string['PATTERN'][key])


def string_analyzier(pattern_elem):
    devide_symbols = []
    devide_symbol = ""
    flag = 0
    max = len(pattern_elem)
    while flag < max:
        if is_critical(pattern_elem[flag]):
            devide_symbol += pattern_elem[flag]
            temp = flag
            while True:
                if ((temp + 1) < max) and (is_critical(pattern_elem[temp + 1])):
                    devide_symbol += pattern_elem[temp + 1]
                    temp += 1
                else:
                    break
            flag = temp + 1
            devide_symbols.append(devide_symbol)
            devide_symbol = ""
        else:
            flag = flag + 1
            continue

    print(devide_symbols)


def is_critical(word):
    if re.match(r'\W', word):
        if word != ' ':
            return True
    elif (word == 'I') | (word == 'N'):
        return True
    else:
        return False
