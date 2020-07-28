import re

from utilities import sparql_query


def entity_recongnition(description):
    description = description.replace("{{", "")
    description = description.replace("}}", "")
    profession = process_string(description)
    return profession


def process_string(description):
    result = []
    words = description.split(' ')
    for word in words:
        if iscapitalize(word):
            profession = find_type(word)
            if profession != "":
                print(profession)
                result.append(profession)
    return result


def find_type(word):
    word = word.strip()
    type_query = "select distinct ?profession where {<http://de.dbpedia.org/resource/" + \
                 word + "> <http://purl.org/dc/terms/subject> ?profession}"
    answer = sparql_query(type_query, "de")
    results = answer['results']['bindings']
    print(results)
    for res in results:
        full_uri = res['profession']['value']
        class_type = full_uri.split("/")[-1]  # e.g Person
        if re.search(r"Beruf|beruf", class_type):
            return "http://de.dbpedia.org/resource/" + \
                 word
    return ""


def iscapitalize(word):
    if len(word) < 1:
        return False
    elif word[0].isupper():
        return True
    else:
        return False
