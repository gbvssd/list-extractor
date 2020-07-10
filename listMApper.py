import urllib
import json
import re
import rdflib
import utilities
import sys
import time
import requests
from mapping_rules import *
from rdflib import RDF, Literal

# defining namespaces to be used in the extracted triples
dbo = rdflib.Namespace("http://dbpedia.org/ontology/")
dbr = rdflib.Namespace("http://dbpedia.org/resource/")
rdf = rdflib.Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")

mapped_domains = []  # used to prevent duplicate mappings
resource_class = ""

# These would contain the mapping rules and the custom defined mapping functions that would be used by the
# mapper functions. These are initially empty and loaded when mapper functions are selected for each resource.
MAPPING = dict()
CUSTOM_MAPPERS = dict()
AVOID = ["Siehe auch", "Literatur", "Einzelnachweise"]
TIME = ["bis", "um", "ca."]


def list_select_mapping(resDict, res, lang, g, pattern):
    """ Calls mapping functions for each matching section of the resource, thus constructing the associated RDF graph.

    Firstly selects the mapping type(s) to apply from ``MAPPING`` (loaded from ``settings.json``) based on resource class (domain).
    If a match is found, it tries to find another match between section names and key-words related to that domain.
    Finally, it applies related mapping functions for the list elements contained in that section.

    :param resDict: dictionary representing current resource.
    :param res: current resource name.
    :param lang: resource language.
    :param g: RDF graph to be created.

    :return: number of list elements actually mapped in the graph.
    """

    # use globally defined dicts
    global mapped_domains
    global resource_class
    global MAPPING
    global CUSTOM_MAPPERS

    if len(MAPPING) == 0:  # load initial configuration
        MAPPING = utilities.load_settings()
        CUSTOM_MAPPERS = utilities.load_custom_mappers()

    # initialize the number of triples extracted
    res_elems = 0

    # if required class is a valid and existing class in the mapping, run suitable mapper functions
    if lang != 'en':  # correct dbpedia resource domain for non-english language
        global dbr
        dbr = rdflib.Namespace("http://" + lang + ".dbpedia.org/resource/")
    db_res = rdflib.URIRef(dbr + res.decode('utf-8'))

    for res_key in resDict.keys():  # iterate on resource dictionary keys
        # print(dk)
        # search for resource keys related to the selected domain
        # if the section hasn't been mapped yet and the title match, apply domain related mapping
        # use the pre-defined mapper functions
        if res_key not in AVOID:
            print(res_key)
            res_elems += map_person_list(resDict[res_key], lang, g, 0, pattern)
        # calls the proper mapping for that domain and counts extracted elements
    return res_elems


def find_info_list(list_elem, g, uri):
    """
    Looks for the information contained in the list element, specific edited for
    https://de.wikipedia.org/wiki/Liste_prominenter_Funkamateure
    applied to pattern 1
    """
    info_list = list_elem.split(",")
    i = 0
    for ele in info_list:
        if i == 1:
            g.add((rdflib.URIRef(uri), dbo["occupation"], Literal(ele)))
        if i == 2:
            g.add((rdflib.URIRef(uri), dbo["callsign"], Literal(ele)))
        i += 1


def find_founded_place(list_elem, g, uri):
    """
    Looks
    for the information contained in the list element, specific edited for
    https://de.wikipedia.org/wiki/Liste_der_Entdecker
    asgined to pattern 2
    """
    info_list = list_elem.split(",")
    i = 0
    for ele in info_list:
        if i == 1:
            g.add((rdflib.URIRef(uri), dbo["birth_place"], Literal(ele)))
        if i == 2:
            g.add((rdflib.URIRef(uri), dbo["founded_place"], Literal(ele)))
        i += 1


def find_birth_place(list_elem, g, uri):
    """
    find the birth place in the text, special for
    https://de.wikipedia.org/wiki/Liste_bekannter_Anarchisten
    in form (birth date "in" birth place ";" death date "in" death place)
    pattern 3
    """

    match = re.search(r'\(.*?;.*?\)', list_elem)
    if match:
        birth_info = match.group(0)
    else:
        return
    ele_list = birth_info.split(";")
    print(ele_list)
    flag = 0
    for ele in ele_list:
        split = ele.split(" in ")
        if len(split) > 1:
            place = split[1]
            place = place.replace("{{", "")
            place = place.replace("}}", "")
            place = place.replace(")", "")
            place = place.replace("(", "")
            if flag == 0:
                print("birth place is")
                print(place)
                g.add((rdflib.URIRef(uri), dbo["birth_place"], Literal(place)))
                flag = 1
                continue
            if flag == 1:
                print("death place is")
                print(place)
                g.add((rdflib.URIRef(uri), dbo["death_place"], Literal(place)))
                flag = 0
                continue
        split = ele.split(" nahe ")
        if len(split) > 1:
            place = split[1]
            place = place.replace("{{", "")
            place = place.replace("}}", "")
            place = place.replace(")", "")
            place = place.replace("(", "")
            if flag == 0:
                print("birth place is")
                print(place)
                g.add((rdflib.URIRef(uri), dbo["birth_place"], Literal(place)))
                flag = 1
                continue
            if flag == 1:
                print("death place is")
                print(place)
                g.add((rdflib.URIRef(uri), dbo["death_place"], Literal(place)))
                flag = 0
                continue


def map_profession_list(list_elem, g, uri):
    """
    find the information about profession in the list element special for
    https://de.wikipedia.org/wiki/Liste_bekannter_Anarchisten
    pattern 3
    """
    match = re.search(r'\)[.,].*', list_elem)
    if match:
        profession = match.group(0)
    else:
        return
    print("profession is")
    print(profession)
    profession = profession.replace(").", "")
    profession = profession.replace("),", "")
    profession = profession.replace(");", "")
    profession = profession.replace("}}", "")
    profession = profession.replace("{{", "")
    g.add((rdflib.URIRef(uri), dbo["profession"], Literal(profession)))


def map_person_list(elem_list, lang, g, elems, pattern):
    for elem in elem_list:

        if type(elem) == list:  # for nested lists (recursively call this function)
            elems += 1
            map_person_list(elem, lang, g, elems, pattern)  # handle recursive lists

        else:
            uri = None
            # elem = elem.encode('utf-8')  # apply utf-8 encoding
            res_name = person_name_map(elem)
            year = month_year_mapper(elem)

            if res_name:
                elem = elem.replace(res_name, "")  # delete resource name found from element for further mapping
                res_name = res_name.replace(" (", '')
                res_name = res_name.replace(" 1", '')
                res_name = res_name.replace(",", '')
                res_name = res_name.replace(' ', '_')
                res_name = res_name.replace("_%E2%80%A0", '')
                if res_name[0] == "_":
                    res_name = res_name[1:]
                if res_name.endswith("_"):
                    res_name = res_name[1:-1]
                print("founded person name ")
                print(res_name)
                print("\n")
                res_name = urllib.request.quote(res_name)
                print("founded year")
                print(year)

                print("\n")
                uri = dbr + res_name
            # add successfully extracted triples into the graph
            if uri and uri != "":
                g.add((rdflib.URIRef(uri), RDF.type, dbo.person))
                if pattern == 1:
                    if year:
                        add_years_to_graph(g, uri, year)
                    find_info_list(elem, g, uri)

                if pattern == 2:
                    if year:
                        add_years_to_graph(g, uri, year)
                    find_founded_place(elem, g, uri)

                if pattern == 3:
                    if year:
                        add_years_to_graph(g, uri, year)
                    find_birth_place(elem, g, uri)
                    map_profession_list(elem, g, uri)

                if pattern == 4:
                    if year:
                        add_year_to_graph(g, uri, year)
                    map_profession_list(elem, g, uri)
                elems += 1

    return elems


def person_list_mapper(list_elem):
    """Looks for a person name inside the element, this mapper is specific for list of person. it should be the word
    before first "("

    :param list_elem: current list element.

    :return: a match if found.
    """
    for ele in TIME:
        list_elem.replace(ele, '')

    match_ref = re.search(r'.*?\,', list_elem)
    if match_ref:
        match_ref = match_ref.group(0)
    else:
        match_ref = list_elem

    temp = match_ref
    match_ref = re.search(r'.*?[0-9]', match_ref)
    if match_ref:
        match_ref = match_ref.group(0)
    else:
        match_ref = temp

    temp = match_ref
    match_ref = re.search(r'.*?\(', match_ref)
    if match_ref:
        match_ref = match_ref.group(0)
    else:
        match_ref = temp

    match_ref = match_ref.replace("{{", "")
    match_ref = match_ref.replace("}}", "")
    match_ref = re.sub(r'\(.*?\)', '', match_ref)
    return match_ref


def add_years_to_graph(g, uri, year, year_ontology={}):
    """Adds all the years related to the URI to the graph g.
    Does not return anything; appends existing graph.

    :param g: current graph.
    :param uri: resource related to the years list.
    :param year: contains a list of years that need to be mapped.
    :param year_ontology: dict containing ontologies that can be used with time periods in a particular domain;

    * Empty dict indicates default values should be taken from y_ontology.
    ``y_ontology = { 'activeYear':'activeYear', 'activeYearsStartDate': 'activeYearsStartDate', 'activeYearsEndDate' : 'activeYearsEndDate'}``
    :return: void
    """

    # default ontologies
    y_ontology = {'activeYear': 'birthDate', 'activeYearsStartDate': 'birthDate',
                  'activeYearsEndDate': 'deathDate'}

    # update if user provides a dictionary to override default ontologies
    for ontology in year_ontology.keys():
        if ontology in y_ontology:
            y_ontology[ontology] = year_ontology[ontology]

    try:
        # start creating triples from years
        if len(year) == 2:
            if "^" in year[0]:  # '^' is a seperator used for month and year
                d = year[0].replace("^", "-")
                g.add((rdflib.URIRef(uri), dbo[y_ontology['activeYearsStartDate']],
                       rdflib.Literal(d, datatype=rdflib.XSD.gYearMonth)))
            else:
                g.add((rdflib.URIRef(uri), dbo[y_ontology['activeYearsStartDate']],
                       rdflib.Literal(year[0], datatype=rdflib.XSD.gYear)))

            if "^" in year[1]:
                d = year[1].replace("^", "-")
                g.add((rdflib.URIRef(uri), dbo[y_ontology['activeYearsEndDate']],
                       rdflib.Literal(d, datatype=rdflib.XSD.gYearMonth)))

            else:
                g.add((rdflib.URIRef(uri), dbo[y_ontology['activeYearsEndDate']],
                       rdflib.Literal(year[1], datatype=rdflib.XSD.gYear)))
            return

        for y in year:
            if type(y) != list:  # Single date (not a time-period)
                if "^" in y:  # '^' is a seperator used for month and year
                    d = y.replace("^", "-")
                    g.add((rdflib.URIRef(uri), dbo[y_ontology['activeYear']],
                           rdflib.Literal(d, datatype=rdflib.XSD.gYearMonth)))

                else:
                    g.add((rdflib.URIRef(uri), dbo[y_ontology['activeYear']],
                           rdflib.Literal(y, datatype=rdflib.XSD.gYear)))

            else:  # if the date is a time period (has a start-end date)
                start_period, end_period = y[0], y[1]
                if "^" in y[0]:  # '^' is a seperator used for month and year
                    d = y[0].replace("^", "-")
                    g.add((rdflib.URIRef(uri), dbo[y_ontology['activeYearsStartDate']],
                           rdflib.Literal(d, datatype=rdflib.XSD.gYearMonth)))
                else:
                    g.add((rdflib.URIRef(uri), dbo[y_ontology['activeYearsStartDate']],
                           rdflib.Literal(y[0], datatype=rdflib.XSD.gYear)))

                if "^" in y[1]:
                    d = y[1].replace("^", "-")
                    g.add((rdflib.URIRef(uri), dbo[y_ontology['activeYearsEndDate']],
                           rdflib.Literal(d, datatype=rdflib.XSD.gYearMonth)))

                else:
                    g.add((rdflib.URIRef(uri), dbo[y_ontology['activeYearsEndDate']],
                           rdflib.Literal(y[1], datatype=rdflib.XSD.gYear)))

    except:
        print('Year exception! Skipping...')
        raise
    return


def year_mapper(list_elem):
    """Looks for a set of exactly 4 digits which would likely represent the year.
    The most basic year extractor, used as a subroutine by ``month_year_mapper()``.

    :param list_elem: current list element.

    :return: a numeric match if found.
    """
    match_num = re.findall(r'[0-9]{4}', list_elem)
    if len(match_num) == 0:
        return None
    return match_num


def month_year_mapper(list_elem):
    """Looks for any kind of date formats; years, month+year or actual date and returns list of dates.

    :param list_elem: current list element.

    :return: a numeric match if found.
    """

    # month_list a dictionaly that contain regex for different months as keys and a corresponding number
    # to that month with a '^' sign as value. This would be useful while mapping the years in the triples.
    month_list = {r'(january\s?)\d{4}': '1^', r'\W(jan\s?)\d{4}': '1^', r'(february\s?)\d{4}': '2^',
                  r'\W(feb\s?)\d{4}': '2^',
                  r'(march\s?)\d{4}': '3^', r'\W(mar\s?)\d{4}': '3^', r'(april\s?)\d{4}': '4^',
                  r'\W(apr\s?)\d{4}': '4^',
                  r'(may\s?)\d{4}': '5^', r'\W(may\s?)\d{4}': '5^', r'(june\s?)\d{4}': '6^', r'\W(jun\s?)\d{4}': '6^',
                  r'(july\s?)\d{4}': '7^', r'\W(jul\s?)\d{4}': '7^', r'(august\s?)\d{4}': '8^',
                  r'\W(aug\s?)\d{4}': '8^',
                  r'(september\s?)\d{4}': '9^', r'\W(sep\s?)\d{4}': '9^', r'\W(sept\s?)\d{4}': '9^',
                  r'(october\s?)\d{4}': '10^',
                  r'\W(oct\s?)\d{4}': '10^', r'(november\s?)\d{4}': '11^', r'\W(nov\s?)\d{4}': '11^',
                  r'(december\s?)\d{4}': '12^', r'\W(dec\s?)\d{4}': '12^'}

    month_present = False
    period_dates = False

    # check if the time period only contains year or if it also contain months
    for mon in month_list:
        if re.search(mon, list_elem, re.IGNORECASE):
            # find and replace the month name with corresponding month code from month_list
            rep = re.search(mon, list_elem, re.IGNORECASE).group(1)
            list_elem = re.sub(rep, month_list[mon], list_elem, flags=re.I)
            month_present = True

    # regex for finding out whether the date consists of a time period or a single year.
    period_regex = r'(?:\(?\d{1,2}\^)?\s?\d{4}\s?(?:–|-)\s?(?:\d{1,2}\^)?\s?\d{4}(?:\))?'

    if re.search(period_regex, list_elem, flags=re.IGNORECASE):
        period_dates = True

    # check for the 4 possible cases of months and time periods

    # if the year doesn't have months or time period, use less complicated year_mapper()
    if month_present == False and period_dates == False:
        return year_mapper(list_elem)

    years = []

    # if only yearly time period is present
    if month_present == False and period_dates == True:
        match_num = re.findall(period_regex, list_elem, flags=re.IGNORECASE)
        if len(match_num) == 0: return year_mapper(list_elem)

        for y in match_num:  # split start and end year
            year = re.split(r'\s?[–-]\s?', y)
            years.append([year[0], year[1]])

        for x in match_num:
            list_elem = list_elem.replace(x, "")

        # append the list of the years and return them
        single_years = year_mapper(list_elem)
        if single_years is not None:
            years.extend(single_years)
        return years

    # if only month is present, no time-periods
    if month_present == True and period_dates == False:
        match_num = re.findall(r'[0-9]{1,2}\^\s?[0-9]{4}', list_elem)
        for x in match_num:
            # replace and format the time period in appropriate form (month^year) and append it int the list
            list_elem = list_elem.replace(x, "")
            x = x.replace(" ", "")
            z = "^".join(x.split('^')[::-1])
            years.append(z)

        single_years = year_mapper(list_elem)
        if single_years is not None:
            years.extend(single_years)
        return years

    else:  # if both months and periods are present
        match_num = re.findall(period_regex, list_elem, flags=re.IGNORECASE)
        if len(match_num) == 0: return year_mapper(list_elem)

        for y in match_num:
            # replace and format the time period in appropriate form [(month^year), (month^year)]
            # and append it int the list
            year = re.split(r'\s?(–|-)\s?', y)
            list_elem = list_elem.replace(y, "")
            years.append(["^".join(year[0].replace(" ", "").split("^")[::-1]),
                          "^".join(year[2].replace(" ", "").split("^")[::-1])])

        single_years = year_mapper(list_elem)
        if single_years is not None:
            years.extend(single_years)
        return years


def person_name_map(elem):
    if elem[0].isdigit():
        if elem[6].isdigit():
            return person_list_mapper(elem[10:])
        else:
            return person_list_mapper(elem[7:])
    else:
        return person_list_mapper(elem)


def add_year_to_graph(g, uri, year):
    """
    this is special edition for https://de.wikipedia.org/wiki/Liste_bekannter_deutscher_USA-Emigranten
    pattern 4
    """
    if len(year) == 2:
        if isinstance(year[0], list):
            if "^" in year[0][1]:  # '^' is a seperator used for month and year
                d = year[0][1].replace("^", "-")
                g.add((rdflib.URIRef(uri), dbo['birthDate'],
                       rdflib.Literal(d, datatype=rdflib.XSD.gYearMonth)))
            else:
                g.add((rdflib.URIRef(uri), dbo['birthDate'],
                       rdflib.Literal(year[0][1], datatype=rdflib.XSD.gYear)))

            if "^" in year[0][1]:
                d = year[0][1].replace("^", "-")
                g.add((rdflib.URIRef(uri), dbo['deathDate'],
                       rdflib.Literal(d, datatype=rdflib.XSD.gYearMonth)))

            else:
                g.add((rdflib.URIRef(uri), dbo['deathDate'],
                       rdflib.Literal(year[0][1], datatype=rdflib.XSD.gYear)))

            if "^" in year[1]:
                d = year[1].replace("^", "-")
                g.add((rdflib.URIRef(uri), dbo['emigrantenDate'],
                       rdflib.Literal(d, datatype=rdflib.XSD.gYearMonth)))

            else:
                g.add((rdflib.URIRef(uri), dbo['emigrantenDate'],
                       rdflib.Literal(year[1], datatype=rdflib.XSD.gYear)))
        else:
            if "^" in year[0]:
                d = year[0].replace("^", "-")
                g.add((rdflib.URIRef(uri), dbo['emigrantenDate'],
                       rdflib.Literal(d, datatype=rdflib.XSD.gYearMonth)))

            else:
                g.add((rdflib.URIRef(uri), dbo['emigrantenDate'],
                       rdflib.Literal(year[0], datatype=rdflib.XSD.gYear)))

            if "^" in year[1]:
                d = year[1].replace("^", "-")
                g.add((rdflib.URIRef(uri), dbo['birthDate'],
                       rdflib.Literal(d, datatype=rdflib.XSD.gYearMonth)))

            else:
                g.add((rdflib.URIRef(uri), dbo['birthDate'],
                       rdflib.Literal(year[1], datatype=rdflib.XSD.gYear)))

    else:
        if isinstance(year[0], list):
            if "^" in year[0][1]:  # '^' is a seperator used for month and year
                d = year[0][1].replace("^", "-")
                g.add((rdflib.URIRef(uri), dbo['birthDate'],
                       rdflib.Literal(d, datatype=rdflib.XSD.gYearMonth)))
            else:
                g.add((rdflib.URIRef(uri), dbo['birthDate'],
                       rdflib.Literal(year[0][1], datatype=rdflib.XSD.gYear)))

            if "^" in year[0][1]:
                d = year[0][1].replace("^", "-")
                g.add((rdflib.URIRef(uri), dbo['deathDate'],
                       rdflib.Literal(d, datatype=rdflib.XSD.gYearMonth)))

            else:
                g.add((rdflib.URIRef(uri), dbo['deathDate'],
                       rdflib.Literal(year[0][1], datatype=rdflib.XSD.gYear)))
        else:
            if "^" in year[0]:
                d = year[0].replace("^", "-")
                g.add((rdflib.URIRef(uri), dbo['birthDate'],
                       rdflib.Literal(d, datatype=rdflib.XSD.gYearMonth)))

            else:
                g.add((rdflib.URIRef(uri), dbo['birthDate'],
                       rdflib.Literal(year[0], datatype=rdflib.XSD.gYear)))
