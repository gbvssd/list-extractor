import json
import re
import sys

pattern_string = dict()
pattern_symbol = list()
property_string = list()


def apply(to_process, pattern):
    load_json()
    pattern_symbol_list = group_process()

    if pattern > len(pattern_symbol):
        print("there is no such pattern")
        sys.exit(0)
    original = pattern_string['PATTERN'][str(pattern)]
    devided_symbol = pattern_symbol_list[pattern - 1]

    # left = to_process
    # original_left = original
    result = dict()

    print(devided_symbol)

    flag = -1
    gap = 1
    while flag < len(devided_symbol):
        # print("the" + str(flag) + "loop begin")
        print("to process string is " + to_process + "\n")

        first = ""
        second = ""
        if flag == -1:
            second = devided_symbol[0]
        elif flag == len(devided_symbol) - 1:
            first = devided_symbol[flag]
        else:
            first = devided_symbol[flag]
            second = devided_symbol[flag + 1]

        # print("the first symbol is" + first + "and the second is " + second + "\n")
        pattern = re.escape(first.upper()) + r".*?" + re.escape(second.upper())
        # print("the pattern is " + pattern + "\n")
        match = re.search(pattern, original)
        proprity = ""

        if match:
            proprity = match.group(0)
            original = original.replace(proprity, '')
            original = second + original
            if proprity == "":
                continue
        print("proprity  is : " + proprity + "\n")
        content = ""

        if (flag + gap) >= len(devided_symbol):
            content = to_process
            print("content is :" + content + "\n")
            break
        elif flag == -1:
            second = devided_symbol[0]
        elif flag == len(devided_symbol) - 1:
            first = devided_symbol[flag]
        else:
            first = devided_symbol[flag]
            second = devided_symbol[flag + gap]

        express = reguler_generate(first, second, proprity)
        print("the express is " + express + "\n")
        match = re.search(express, to_process)
        if match:
            content = match.group(0)
            print("content is :" + content + "\n")
            to_process = second + to_process
            flag = flag + gap
            gap = 1
            if content == "":
                continue
        else:
            gap += 1
            continue
        to_process = to_process.replace(content, '')
        print("----------------------------------------------------------")

    # flag = 0
    # for symbol in reversed(devided_symbol):
    #   if flag == len(devided_symbol) - 1:
    #        original_right = original_left.rsplit(symbol, 1)[1]
    #        original_left = original_left.rsplit(symbol, 1)[0]
    #        if len(left.split(symbol, 1)) < 2:
    #            continue
    #        right = left.rsplit(symbol, 1)[1]
    #        left = left.rsplit(symbol, 1)[0]
    #        result[original_right] = right
    #        result[original_left] = left
    #    else:
    #        if symbol.islower():
    #            symbol = symbol.upper()
    #        original_right = original_left.rsplit(symbol, 1)[1]
    #        original_left = original_left.rsplit(symbol, 1)[0]
    #        print("symbol is :" + symbol)
    #        print("proprity is :" + original_right)
    #        print("what left is :" + original_left)
    #        symbol = symbol.lower()
    #        if len(left.split(symbol, 1)) < 2:
    #            flag += 1
    #            print("invaild symbol" + symbol)
    #            continue
    #        else:
    #            right = left.rsplit(symbol, 1)[1]
    #            left = left.rsplit(symbol, 1)[0]
    #            print("value is :" + right)
    #            result[original_right] = right
    #    flag += 1

    print(result)
    print("\n\n\n\n")
    return result


def reguler_generate(first_symbol, second_symbol, middle_string):
    result = ""
    first_symbol = re.escape(first_symbol)
    second_symbol = re.escape(second_symbol)
    print("the symbol is:" + first_symbol + "  and  " + second_symbol)
    match = re.search(r"name", middle_string)
    if match:
        print("it contain a name")
        result = first_symbol + r".*?\{\{.*?\}\}.*?" + second_symbol
        return result

    match = re.search(r"Date|date", middle_string)
    if match:
        print("it contain a date")
        result = first_symbol + r".*?" + second_symbol
        return result

    result = first_symbol + r".*?" + second_symbol
    return result


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
    global pattern_symbol

    load_json()
    for key in pattern_string['PATTERN']:
        # print("analyzer " + key + "from :" + pattern_string['PATTERN'][key])
        pattern_symbol.append(string_analyzier(pattern_string['PATTERN'][key]))

    return pattern_symbol


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

            if devide_symbol == "IN":
                devide_symbol = " IN "
            if devide_symbol.islower():
                devide_symbols.append(devide_symbol)
            else:
                devide_symbols.append(devide_symbol.lower())

            devide_symbol = ""
        else:
            flag = flag + 1
            continue

    # print(devide_symbols)
    return devide_symbols


def is_critical(word):
    if re.match(r'\W', word):
        if word != ' ':
            return True
    elif (word == 'I') | (word == 'N'):
        return True
    else:
        return False
