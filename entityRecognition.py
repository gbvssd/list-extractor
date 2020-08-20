import re

from utilities import sparql_query


def entity_recongnition(description, entity_property):
    """
    pre process the string remove special character and find the corresponded resource in DBpedia

    :param description: the string that to process
    :param entity_property: the property of the the string

    :return: the list of resource URI
    """
    description = description.replace("{{", "")
    description = description.replace("}}", "")
    description = description.replace(")", "")
    description = description.replace(",", "")
    description = description.strip()
    profession = process_string(description, entity_property)
    return profession


def process_string(description, entity_property):
    """
    find the word which is a noun and search in the data base

    :param description: the string that contains words
    :param entity_property :
    :return : a list of resource URI
    """
    result = []
    words = description.split(' ')
    match = re.search(r"profession", entity_property)
    if match:
        print("it is a profession")
        for word in words:
            if iscapitalize(word):
                print("examing if word " + word + "is a profession")
                profession = find_type(word)
                if profession != "":
                    print(profession)
                    result.append(profession)
    else:
        match = re.search(r"[Place|place]", entity_property)
        if match:
            for word in words:
                if iscapitalize(word):
                    location = find_location(word)
                    if location != "":
                        print(location)
                        result.append(location)
    return result


def find_type(word):
    """
    look into the DBpedia Datebase to find out if the word is a profession
    """
    word = word.strip()
    type_query = "select distinct ?profession where {<http://de.dbpedia.org/resource/" + \
                 word + "> <http://purl.org/dc/terms/subject> ?profession}"
    answer = sparql_query(type_query, "de")
    results = answer['results']['bindings']
    for res in results:
        full_uri = res['profession']['value']
        class_type = full_uri.split("/")[-1]  # e.g Person
        if re.search(r"Beruf|beruf", class_type):
            return "http://de.dbpedia.org/resource/" + \
                   word
    return ""


def iscapitalize(word):
    """
    find out if the word start with a upper character
    """
    if len(word) < 1:
        return False
    elif word[0].isupper():
        return True
    else:
        return False


def find_location(word):
    """
    lookup in the DBpedia datebase to find the location with given string
    """
    location = word.strip()
    location = location.replace(",", "")
    type_query = "select ?location where { ?location rdfs:label \"" + location + "\"@de." \
                                                                                 "?location a dbo:Location.}LIMIT 100"
    answer = sparql_query(type_query, "de")
    results = answer['results']['bindings']
    if len(results) > 0:
        res = results[0]
        full_uri = res['location']['value']
        location_name = full_uri.split("/")[-1]  # e.g Person
        return "http://de.dbpedia.org/resource/" + \
               location_name
    else:
        return ""
