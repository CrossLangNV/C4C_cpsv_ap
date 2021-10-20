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
* [ ] Can we validate the data?
