import warnings
from typing import List

import requests

from connectors.term_extraction_utils.cas_utils import CasWrapper
from connectors.term_extraction_utils.models import ChunkModel, ContactInfo, TermsModel, Document

KEY_CAS_CONTENT = 'cas_content'


class ConnectorTermExtraction:
    """
    Connects to the Term Extraction API
    """

    _PATH_EXTRACT_TERMS = "/extract_terms"

    def __init__(self, url,
                 test_connection: bool = True):
        """

        Args:
            url:
                URL of the API
            test_connection:
                flag to make a small connection check. Disable for slightly faster init.
        """

        self.url = url  # TODO remove rightsided slashes? google.com/ -> google.com

        if test_connection:
            try:
                requests.get(url)
            except requests.exceptions.ConnectionError as e:
                warnings.warn(f"Can't reach API.\n{e}", ConnectionWarning)

    def get_contact_info(self,
                         html: str,
                         language: str = None,
                         unique: bool = True) -> List[str]:
        """
        Extracts the contact info from a webpage.

        Args:
            html: HTML of a webpage, classified as containing a public service procedure.
            language:
                en, fr, de...

        Returns:
            contact info, saved as list of strings.
        """

        contact_info_response = self._post_extract_contact_info(html,
                                                                language=language)

        # TODO use cleaned version of contact
        # TODO test that cleaned version returns the same values.

        cas = CasWrapper.from_cas_content(contact_info_response.cas_content)

        l_contact = cas.get_contact_paragraph(unique=unique)

        return l_contact

    def get_terms(self, html: str,
                  language: str = "en") -> List[str]:

        terms_return = self._post_extract_terms(html,
                                                language=language)

        cas = CasWrapper.from_cas_content(terms_return.cas_content)

        # TODO use cleaned list of terms/lemmas
        l_terms = cas._get_tokens()

        return l_terms

    def _post_chunking(self,
                       html: str,
                       language: str = None):

        doc = Document(html=html,
                       language=language
                       )

        r = requests.post(self.url + "/chunking",
                          json=doc.dict())
        j_r = r.json()

        chunk = ChunkModel.from_json(j_r)

        return chunk

    def _post_extract_terms(self, html: str,
                            language: str = "en") -> TermsModel:
        """

        Args:
            html:
            language: In this post request, it is required to provide the language code.

        Returns:

        """

        if language is None:
            warnings.warn("Language should be not-None", UserWarning)

        doc = Document(html=html,
                       language=language
                       )

        r = requests.post(self.url + self._PATH_EXTRACT_TERMS,
                          json=doc.dict())
        j_r = r.json()
        return TermsModel.from_json(j_r)

    def _post_extract_contact_info(self,
                                   html: str,
                                   language: str = None) -> ContactInfo:
        """
        Post request for Contact Info Extraction.

        Args:
            html: HTML of a webpage, classified as containing a public service procedure.
            language:
                en, fr, de...

        Returns:
            json
        """

        doc = Document(html=html,
                       language=language
                       )

        r = requests.post(self.url + "/extract_contact_info",
                          json=doc.dict())
        j_r = r.json()

        contact_info_response = ContactInfo(**j_r)

        return contact_info_response

    def _post_extract_questions_answers(self, html: str,
                                        language: str = None):
        """
        TODO
        Returns:

        """
        raise NotImplementedError()
        doc = Document(html=html,
                       language=language
                       )

        r = requests.post(self.url + "/extract_contact_info",
                          json=doc.dict())
        j_r = r.json()
        return


class ConnectionWarning(Warning):
    """
    Custom warning when the connection might be lost.
    """
