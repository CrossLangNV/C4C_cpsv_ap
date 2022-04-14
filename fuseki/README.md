# README

We encountered a problem before with the stain/jena-fuseki image where it raises an error:

```
Server     ERROR Exception in initialization: Process ID 7 can't open database at location /fuseki/system/ because it is already locked by the process with PID 8. TDB databases do not permit concurrent usage across JVMs so in order to prevent possible data corruption you cannot open this location from the JVM that does not own the lock for the dataset
fuseki_1  | [2020-03-11 16:44:57] WebAppContext WARN  Failed startup of context o.e.j.w.WebAppContext@1a28aef1{Apache Jena Fuseki Server,/,file:///jena-fuseki/webapp/,UNAVAILABLE}
fuseki_1  | org.apache.jena.tdb.TDBException: Process ID 7 can't open database at location /fuseki/system/ because it is already locked by the process with PID 8. TDB databases do not permit concurrent usage across JVMs so in order to prevent possible data corruption you cannot open this location from the JVM that does not own the lock for the dataset
```

The [Dockerfile](./Dockerfile) here implements the fix based on:
https://github.com/stain/jena-docker/issues/34#issuecomment-846905725

## Example queries

* Return all triples available in multiple languages

```
SELECT ?subject 
	?predicate
	(GROUP_CONCAT( CONCAT('"',?literal,'"@',lang(?literal)); separator=" | " ) as ?label)

WHERE {
  ?subject ?predicate ?literal .
  
  FILTER(!LANGMATCHES(LANG(?literal), ''))
}

GROUP BY ?subject ?predicate
HAVING (COUNT(*) >= 2)
ORDER BY ?subject ?predicate
LIMIT 50
```
