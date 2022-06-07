# DEMO V-ICT-OR

## TODO

Websites

* Scrape [Berlara](https://www.berlare.be/sitemap.aspx).

Example (https://www.berlare.be/adreswijziging-binnen-berlare_2.html)

```commandline
docker compose run cpsv_ap python scripts/extract_cpsv_ap.py -g -o scripts/V_ICT_OR/example1.rdf --html_parsing scripts/V_ICT_OR/example1.html -l NL -c BE -m https://www.berlare.be/adreswijziging-binnen-berlare_2.html 
```

(extra options)

```commandline
 --translate NL EN FR DE
```

languages

* [ ] Nl, En, Fr, De
* [ ] Add Greek
* [ ] Ukrainian
