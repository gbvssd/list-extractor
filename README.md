# List-extractor - Extract Data from Wikipedia Lists

List-Extractor is a tool that can *extract information from wikipedia lists and form appropriate RDF triples from the list data.*

#### [GSoC'16 Detailed Progress available here](https://github.com/dbpedia/extraction-framework/wiki/GSoC_2016_Progress_Federica)
#### [Final commit of GSoC'16 can be found here](https://github.com/dbpedia/list-extractor/tree/55abff51634324bb657f531fe2e3bb699dfada74)
#### [GSoC'17 Work's detailed progress available here](https://github.com/dbpedia/list-extractor/wiki/GSoC-2017:-Krishanu-Konar-progress)
#### [List-Extractor wiki available here](https://github.com/dbpedia/list-extractor/wiki)
#### [GSoC'17 Final results and challenges available here](https://github.com/dbpedia/list-extractor/wiki/GSoC-2017:-Krishanu-Konar-progress#results)


## How to run the tools

This project contains 2 differnt tools: `List-Extractor` and `Rules-Generator`.
Use `rulesGenerator.py` first to generate desired rules, and then use `listExtractor.py` to extract triples for wiki resources.
Alternatively, you can use only `listExtractor.py` and extract with existing default settings.

For more details, refer to the documentation present in the `docs` folder. The sample generated datasets can be found **[here](https://drive.google.com/open?id=0BzDWYUiB6LUTYzdFU19BX2lUMjA).** Some example triples for different domains are present in `extracted` folder.

### List-Extractor:

`python listExtractor.py [collect_mode] [source] [language] [-c class_name]`

* `collect_mode` : `s` or `a`

    * use `s` to specify a single resource or `a` for a class of resources in the next parameter.

* `source`: a string representing a class of resources from DBpedia ontology (find supported domains below), or a single Wikipedia page of an actor/writer.

* `language`: `en`, `it`, `de` etc. (for now, available only for some languages, for selected domains)

    * a two-letter prefix corresponding to the desired language of Wikipedia pages and SPARQL endpoint to be queried.

* `-c --classname`: a string representing classnames you want to associate your resource with. Applicable only for `collect_mode="s"`. 

**NOTE:** While extracting triples from multiple resources in a domain (`collect_mode = a`), using `Ctrl + C` will skip the current resource and move on to the next resource. To quit the extractor, use `Ctrl + \`.

## Examples: 

* `python listExtractor.py a Writer it` 
* `python listExtractor.py s William_Gibson en` : Uses the default inbuilt mapper-functions
* `python listExtractor.py s William_Gibson en -c CUSTOM_WRITER` : Uses the `CUSTOM_WRITER` mapping only to extract list elements.

If successful, a .ttl file containing RDF statements about the specified source is created inside a subdirectory called `extracted`.

### Rules-Generator:

`python rulesGenerator.py`

* This is an interactive tool, select the options given in the menu for using the rules generator.
* While creating new mapping rules or mapper functions, make sure to follow the required format as suggested by the tool.
* Upon successful addition/modification, it will update the `settings.json` and `custom_mapper.json` so that the new user defined rules/functions can run with extractor.

## Default Mapped Domains:

* English (`en`):
    * **Person**: `Writer`, `Actor`, `MusicalArtist`, `Athelete`, `Polititcian`, `Manager`, `Coach`, `Celebrity` etc.
    * **EducationalInstitution**: `University`, `School`, `College`, `Library`
    * **PeriodicalLiterature**: `Magazines`, `Newspapers`, `AcademicJournals`
    * **Group**: `Band`

* Other (`it`, `de`, `es`):
    * `Writer`, `Actor`, `MusicalArtist`

* More Domains can be added using the `rulesGenerator.py` tool.

### Attributions for 3rd party tools:

This project uses 2 other existing open source projects.

* **JSONpedia**, a framework designed to simplify access at MediaWiki contents transforming everything into JSON. Such framework provides a library, a REST service and CLI tools to parse, convert, enrich and store WikiText documents. 

The software is copyright of Michele Mostarda (me@michelemostarda.it) and released under Apache 2 License.
Link : [JSONpedia](https://bitbucket.org/hardest/jsonpedia)

* **JCommander**,  a very small Java framework that makes it trivial to parse command line parameters. 

Contact Cédric Beust (cedric@beust.com) for more information. Released under Apache 2 License.
Link : [JCommander](https://github.com/cbeust/jcommander)


### Requirements
* [Python 2.7](https://www.python.org/download/releases/2.7/) 
* [RDFlib library](http://rdflib.readthedocs.io/en/stable/gettingstarted.html)
* Stable internet connection

