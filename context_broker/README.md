* Need arg: "id"

Notes converting JSON-LD to NGSI-LD:

* In general URI's have to be converted to URN's: Don't forget to add the namespace to @context.
    * Also values! e.g. value for id.
* **id** and **type** idea are required.
    * The @ in @type and @id can stay in the key of the first dictionary, not in sub-dictionaries
    * Remove @ in other keys
    * Add **{"type": "Property"}** next to the value of Literals:

* [ ] [Adding multiple items](https://fiware-tutorials.readthedocs.io/en/latest/crud-operations.html#batch-create-new-data-entities-or-attributes)
* [ ] !How to retrieve context? For the id we don't retrieve the namespace.
* [ ] Can we validate the
  data? [TODO research this link.](https://fiware-tutorials.readthedocs.io/en/latest/administrating-xacml.html)

# Namespaces

| Prefix | Namespace |
|---|---|
| cv | http://data.europa.eu/m8g/ |
| cpsv | http://purl.org/vocab/cpsv# |
| adms | http://www.w3.org/ns/adms# |
| eli | http://data.europa.eu/eli/ontolog |
| dct | http://purl.org/dc/terms/ |
| dcat | http://www.w3.org/ns/dcat# |
| skos | http://www.w3.org/2004/02/sko |
| schema | http://schema.org/ |
| locn | http://www.w3.org/ns/locn# |
| foaf | http://xmlns.com/foaf/0.1/ |

## CPSV-AP

For the data scheme, the following files could be useful:

- Contains
  @context [https://github.com/catalogue-of-services-isa/CPSV-AP/blob/master/releases/2.2.1/CPSV-AP_v2.2.1.jsonld](https://github.com/catalogue-of-services-isa/CPSV-AP/blob/master/releases/2.2.1/CPSV-AP_v2.2.1.jsonld)
- [https://github.com/catalogue-of-services-isa/CPSV-AP/blob/master/releases/2.2.1/SC2015DI07446_D02.02_CPSV-AP_v2.2.1_RDF_Schema_v1.00.ttl](https://github.com/catalogue-of-services-isa/CPSV-AP/blob/master/releases/2.2.1/SC2015DI07446_D02.02_CPSV-AP_v2.2.1_RDF_Schema_v1.00.ttl)
