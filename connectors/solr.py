import os
from typing import Dict, List, Optional

import pysolr
from pydantic import BaseModel, validator
from requests.auth import HTTPBasicAuth

SOLR_LOGIN = os.environ.get("SOLR_LOGIN")
SOLR_PASSW = os.environ.get("SOLR_PASSW")


class Result(BaseModel):
    """
    Results as returned by querying our SOLR server.
    """
    url: Optional[str]
    title: Optional[str]
    website: Optional[str]  # Municipality
    date: Optional[str]  # Data of scraping
    language: Optional[str]  # Source language
    pdf_docs: Optional[List[str]]  # (truely optional)
    id: Optional[str]
    file_url: Optional[List[str]]  # (truely optional)
    file_name: Optional[List[str]]  # (truely optional)
    date_last_update: Optional[str]
    content: Optional[str]  # Parsed data
    accepted_probability: Optional[str]  # Admnistrative procedure
    acceptance_state: Optional[str]  # Rounded probablity: "Accepted" or "not Accepted"
    content_html: Optional[str]  # Raw HTML
    _version_: Optional[str]

    @validator("url",
               "title",
               "website",
               "date",
               "content",
               "content_html",
               "accepted_probability",
               "acceptance_state",
               pre=True)
    def remove_list(cls, v):
        if isinstance(v, list) and len(v):
            # Get single entity from list
            return v[0]

        return v


class SOLRConnector(pysolr.Solr):
    def __init__(self, base_url="https://solr.cefat4cities.crosslang.com/solr/documents/", *args, **kwargs):
        super(SOLRConnector, self).__init__(base_url,
                                            # always_commit=True,
                                            # timeout=10,
                                            auth=HTTPBasicAuth(SOLR_LOGIN, SOLR_PASSW),
                                            *args, **kwargs)

        # Do a health check.
        self.ping()

    def _get_accepted(self, debug=False) -> List[Result]:
        results = self.search(q="acceptance_state:Accepted")

        if debug:
            for result in results:
                print(result)

        return list(map(lambda d: Result(**d), results))

    def get_different_languages(self,
                                acceptance_state: bool = None) -> Dict[str, int]:
        """
        Get the different source languages found in the SOLR database.

        Returns:

        """

        params_facet = {
            'facet': 'true',
            'facet.limit': 100,
            'facet.mincount': 1,
            'facet.sort': 'count',
            'facet.field': ['language'],
            'fl': '*',
        }

        def get_q(acceptance_state: bool):

            if acceptance_state is not None:
                if bool(acceptance_state):
                    q = "acceptance_state:Accepted"
                else:
                    q = "acceptance_state:Rejected"
                return q

            q = "*:*"
            return q

        def parse_language_facet(results: pysolr.Results) -> dict:
            facet_fields = results.facets['facet_fields']
            facet_language = facet_fields["language"]
            d_lang = {}
            for lang, n in zip(facet_language[::2], facet_language[1::2]):
                d_lang[lang] = n

            return d_lang

        q = get_q(acceptance_state=acceptance_state)

        results = self.search(q=q,
                              **params_facet)

        d_lang = parse_language_facet(results)

        return d_lang
