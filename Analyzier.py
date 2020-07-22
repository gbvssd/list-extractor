import json
import re
import sys

pattern_string = dict()
pattern_symbol = list()


def apply(to_process, pattern):
    """
        apply the pattern to the string

        :param to_process: this is the string that the pattern should be applied to
        :param pattern: this is the pattern number, which corresponded to a pattern in ''pattern.json'' file
        :return : void
    """
    load_json()
    pattern_symbol_list = group_process()

    if pattern > len(pattern_symbol):
        print("there is no such pattern")
        sys.exit(0)

    devided_symbol = pattern_symbol_list[pattern - 1]
    result = dict()
    print(devided_symbol)

    property_list = find_property(pattern, pattern_symbol_list)

    number = 0
    flag = -1
    gap = 1
    skip = 0
    while flag < len(devided_symbol):
        # print("the" + str(flag) + "loop begin")
        # print("to process string is " + to_process + "\n")
        content = ""

        first = ""
        second = ""
        if (flag + gap) >= len(devided_symbol) or number > len(property_list):
            content = to_process
            # print("content is :" + content + "\n")
            result[clear_text(property_list[-1])] = content
            break
        elif flag == -1:
            second = devided_symbol[flag + gap]
        elif flag == len(devided_symbol) - 1:
            first = devided_symbol[flag]
        else:
            first = devided_symbol[flag]
            second = devided_symbol[flag + gap]

        express = reguler_generate(first, second, property_list[number])
        # print("the express is " + express + "\n")
        match = re.search(express, to_process)
        if match:
            content = match.group(0)
            # print("content is :" + content + "\n")
            result[clear_text(property_list[number])] = content
            number += 1
            number += skip
            to_process = second + to_process
            flag = flag + gap
            gap = 1
            if content == "":
                continue
        else:
            gap += 1
            skip += 1
            continue
        to_process = to_process.replace(content, '')
        # print("----------------------------------------------------------")

    print(result)
    print("\n\n\n\n")
    return result


def clear_text(text):
    """
    clear the symbol in the text, make it only contain the useful information

    :param text: the text to be cleared
    :return : the cleared text
    """
    result = ""
    for char in text:
        if is_critical(char):
            continue
        else:
            result += char
    return result


def find_property(pattern, pattern_symbol_list):
    """
    this function will find the property name in the pattern string

    :param pattern: the number of the pattern
    :param pattern_symbol_list: the list of pattern symbol corresponed to the ''pattern.json'' file

    :return : a list of property name
    """
    original = pattern_string['PATTERN'][str(pattern)]
    devided_symbol = pattern_symbol_list[pattern - 1]

    result = list()
    flag = -1
    while flag < len(devided_symbol):
        first = ""
        second = ""
        if flag == -1:
            second = devided_symbol[0]
        elif flag == len(devided_symbol) - 1:
            first = devided_symbol[flag]
        else:
            first = devided_symbol[flag]
            second = devided_symbol[flag + 1]

        pattern = re.escape(first.upper()) + r".*?" + re.escape(second.upper())
        match = re.search(pattern, original)
        proprity = ""

        if flag == len(devided_symbol) - 1:
            result.append(original)
            break

        if match:
            proprity = match.group(0)
            result.append(proprity)
            original = original.replace(proprity, '')
            original = second.upper() + original
            if proprity == "":
                continue
        flag += 1

    return result


def reguler_generate(first_symbol, second_symbol, middle_string):
    result = ""
    first_symbol = re.escape(first_symbol)
    second_symbol = re.escape(second_symbol)
    # print("the symbol is:" + first_symbol + "  and  " + second_symbol + "\n")
    # print("what within is  " + middle_string + "\n")
    match = re.search(r"name", middle_string)
    if match:
        # print("it contain a name")
        result = first_symbol + r".*?\{\{.*?\}\}.*?" + second_symbol
        return result

    match = re.search(r"Date|date", middle_string)
    if match:
        # print("it contain a date")
        result = first_symbol + r".+?[0-9]+.*?" + second_symbol
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
        return True
    elif (word == 'I') | (word == 'N'):
        return True
    else:
        return False
