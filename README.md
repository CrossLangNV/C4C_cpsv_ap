# C4C_cpsv_ap

One of the goals is to export the data to open linked data format.

This can be separated into subproblems:

* Convert website to **Machine Readable** data.
* Extract relevant information.
* Save as RDF.

  ![CPSV-AP PNG](examples/CPSV-AP.png)
  *Core Public Service Vocabulary Application Profile*

## TODO

*[ ] Extract and save basic functionalities
    * Opening hours
    * Evidence
    * Criterion Requirements
    * Contact Point

# Packages

Get python RDF parser for SKOS:Concepts

    pip install git+https://github.com/CrossLangNV/DGFISMA_RDF@development

Example code to generate RDFLib graph for the concepts:

    from concepts.build_rdf import ConceptGraph

    ConceptGraph(['term 1', 'term 2'])

# Data

* Dienstencataloog
  Vlaanderen [https://data.vlaanderen.be/doc/applicatieprofiel/dienstencataloog/](https://data.vlaanderen.be/doc/applicatieprofiel/dienstencataloog/)

    * example RDF
      [https://data.vlaanderen.be/context/dienstencataloog.jsonld](https://data.vlaanderen.be/context/dienstencataloog.jsonld)

* [https://github.com/catalogue-of-services-isa/RDF_transformation](https://github.com/catalogue-of-services-isa/RDF_transformation)

# Other sources

The following services are found
on [https://github.com/catalogue-of-services-isa](https://github.com/catalogue-of-services-isa)

* Still have to check it, but a harvester for CPSV-AP data.
  [https://github.com/catalogue-of-services-isa/cpsv-ap_harvester](https://github.com/catalogue-of-services-isa/cpsv-ap_harvester)

* [cpsv-ap_validator](https://github.com/catalogue-of-services-isa/cpsv-ap_validator): Got it up and running. Has a nice
  document in doc/ that explains well the content of CPSV models. Usefulness will come when we have our own data.

* [https://github.com/catalogue-of-services-isa/Trento_conversionToRDF](https://github.com/catalogue-of-services-isa/Trento_conversionToRDF)
  RDF data from Trento, Italy.

* Example of API around the
  RDF: [http://cpsv-ap.semic.eu:8890/cpsv-ap_editor/browse-all-content](http://cpsv-ap.semic.eu:8890/cpsv-ap_editor/browse-all-content)