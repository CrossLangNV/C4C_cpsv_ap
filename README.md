<table cellspacing="0" cellpadding="0">
    <tr>
        <td><img src="https://user-images.githubusercontent.com/8747446/160939167-1e70640f-ba7d-48fa-93a3-7167520fbbd7.png" width="300"></td>
        <td><img src="https://user-images.githubusercontent.com/8747446/160938749-10b34fed-c9e8-4644-8218-2d61fcae5299.png" width="400"></td>
    </tr>
</table>

# CPSV-AP Extraction Pipeline

One of the goals is to export the data to open linked data format.

This can be separated into subproblems:

* Convert website to **Machine Readable** data.
* Extract relevant information.
* Save as RDF.

![image](https://user-images.githubusercontent.com/8747446/161078291-803b78de-b4f9-414f-aa53-3c444fd7e671.png)
  *Core Public Service Vocabulary Application Profile*

For all information related to CPSV-AP
see [Core Public Service Vocabulary Application Profile solution](https://joinup.ec.europa.eu/collection/semantic-interoperability-community-semic/solution/core-public-service-vocabulary-application-profile/releases)

## Relation extraction

To extract the relations as defined by the CPSV-AP, a CLI can be found
in [scripts/extract_cpsv_ap.py](scripts/extract_cpsv_ap.py).

This CLI can be used after building the images with our docker-compose file.

> docker compose run cpsv_ap python scripts/extract_cpsv_ap.py -h

![image](https://user-images.githubusercontent.com/8747446/161078551-6ce66a33-9fe5-4619-af65-b711cac44632.png)

An example to run the extraction:

> docker compose run cpsv_ap python scripts/extract_cpsv_ap.py -g -o scripts/DEMO_BELGIUM_GENERAL.rdf -l NL -c BE -m http://stad.gent scripts/DEMO_PROCEDURE.html

The output is saved in [tests/scripts/examples/DEMO_PROCEDURE.html](tests/scripts/examples/DEMO_PROCEDURE.html) and can
be visualized with [RDF Grapher](https://www.ldf.fi/service/rdf-grapher):

![Visualisation of extracted CPSV-AP RDF](https://user-images.githubusercontent.com/8747446/161078882-eae61bd5-1348-4be8-bb9c-b38b72b75c07.png)

## Validation

For validation of the RDF, we currently refer
to [https://www.itb.ec.europa.eu/shacl/cpsv-ap/upload](https://www.itb.ec.europa.eu/shacl/cpsv-ap/upload).

Validation of the data (07/10/2011):

* data/output/demo2_export.rdf: property dct:spatial has to be added to PublicOrganisations.
* data/examples/trento.jsonld: flawless
* data/examples/export.rdf: "The property dct:language SHOULD have the following pattern"

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

# Connector

In order to make the connector work, make sure to first have a RDF enpoint available and added to [environment file](secrets/cpsv_ap.env)

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
