import argparse
import re
import sys

import rdflib
import logging

logging.getLogger("rdflib").setLevel(logging.ERROR)

from utilities import sparql_query

g = rdflib.Graph()


def show_tripple():
    for subject, predicate, objection in g:
        print(subject)
        print(predicate)
        print(objection)
        print("--------------------------")


def evaluate_val():
    total_number = 0
    val_number = 0
    for subject, predicate, objection in g:
        if "http://dbpedia.org/ontology/birthDate" not in predicate \
                and "http://dbpedia.org/ontology/deathDate" not in predicate \
                and "http://www.w3.org/1999/02/22-rdf-syntax-ns#type" not in predicate:
            print(predicate)
            total_number += 1
            if "http://" in objection:
                # print(objection)
                val_number += 1
    print(str(val_number) + "/" + str(total_number))
    return val_number / total_number


def evaluate_eff():
    result = set()
    total_number = 0
    eff_number = 0
    for subject, predicate, objection in g:
        if "http://www.w3.org/1999/02/22-rdf-syntax-ns#type" in predicate:
            print("evaluating " + subject)
            temp = eff_number
            total_number += 1
            type_query = "select distinct ?profession where {<" + subject + "> a ?profession}"
            answer = sparql_query(type_query, "de")
            results = answer['results']['bindings']
            # print(results)
            for res in results:
                full_uri = res['profession']['value']
                class_type = full_uri.split("/")[-1]  # e.g Person
                if re.search(r"Person|person", class_type):
                    eff_number += 1
                    break
            if eff_number != temp + 1:
                type_query = "select distinct ?profession where {<" + subject + "> <http://dbpedia.org/ontology" \
                                                                                "/wikiPageRedirects> ?profession} "
                answer = sparql_query(type_query, "de")
                results = answer['results']['bindings']
                # print(results)
                if results:
                    res = results[0]
                    full_uri = res['profession']['value']
                    type_query = "select distinct ?profession where {<" + full_uri + "> a ?profession} "
                    answer = sparql_query(type_query, "de")
                    results = answer['results']['bindings']
                    for res in results:
                        full_uri = res['profession']['value']
                        class_type = full_uri.split("/")[-1]  # e.g Person
                        if re.search(r"Person|person", class_type):
                            eff_number += 1
                            break
                if eff_number != temp + 1:
                    result.add(subject)
        else:
            continue
    print(str(eff_number) + "/" + str(total_number))
    return result


def evaluate_cor():
    date_element = 0
    location_element = 0
    date_correct = 0
    location_correct = 0
    for subject, predicate, objection in g:
        if "Date" in predicate or "date" in predicate:
            date_element += 1
            type_query = "select distinct ?date where {<" + subject + "> " + "<" + predicate + "> ?date}"
            answer = sparql_query(type_query, "de")
            results = answer['results']['bindings']
            if results:
                res = results[0]
                date = res['date']['value']
                print("-----------------------------")
                print("subject is " + subject)
                print("Date in graph is " + objection)
                print("Date in DBpedia is " + date)
                print("-----------------------------")
                if "YearMonth" in objection.n3():
                    if objection.split("-")[0] == date.split("-")[0] and objection.split("-")[1] == date.split("-")[1]:
                        date_correct += 1
                        continue
                elif "Year" in objection.n3():
                    if objection.split("-")[0] == date.split("-")[0]:
                        date_correct += 1
                        continue
            else:
                date_correct += 1
        if "Place" in predicate:

            print("-----------------------------")
            print("subject is " + subject)
            print("location in graph is " + objection)
            location_element += 1
            type_query = "select distinct ?location where {<" + subject + "> " + "<" + predicate + "> ?location}"
            answer = sparql_query(type_query, "de")
            results = answer['results']['bindings']
            if results:
                for res in results:
                    location_uri = res['location']['value']
                    print("location in DBpeida is " + location_uri)
                    print("-----------------------------")
                    if location_uri in objection:
                        location_correct += 1
                        print("location match")
                        break
            else:
                location_correct += 1
    print("date correct is" + str(date_correct) + "/" + str(date_element))
    print("location correct is" + str(location_correct) + "/" + str(location_element))


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

    parser.add_argument('source', type=str,
                        help='Select the RDF file you want to evaluate')
    args = parser.parse_args()

    g.bind("dbo", "http://dbpedia.org/ontology/")
    g.bind("dbr", "http://dbpedia.org/resource/")

    file_path = "/Users/apple/list-extractor/extracted/" + args.source

    try:
        print(file_path)
        g.load(file_path, format="ttl")
    except:
        print("no such file")
        sys.exit(0)

    # the prompt message
    prompt_str = "Select one of the following options:\n\n" \
                 "1. Showing triple\n" \
                 "2. Evaluate Effectiveness\n" \
                 "3. Evaluate Validation\n" \
                 "4. Evaluate Correct Rate\n" \
                 "0. Quit\n" \
                 "\nYour option: "
    print('')

    # option parser; decides the flow of the program according to what user wants to do.
    while True:
        try:
            # display and accept actions for different options
            run = int(input(prompt_str))
            if run == 1:
                show_tripple()
            elif run == 2:
                res = evaluate_eff()
                for ele in res:
                    print("-------------")
                    print(ele)
                    print("-------------")
            elif run == 3:
                evaluate_val()
            elif run == 4:
                evaluate_cor()
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
