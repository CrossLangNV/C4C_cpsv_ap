import warnings
from typing import List, Union

import requests
from pydantic import BaseModel

from connectors.term_extraction_utils.cas_utils import cas_from_cas_content, CONTACT_PARAGRAPH_TYPE, _get_content
from connectors.term_extraction_utils.models import ChunkModel, ContactInfo

KEY_CAS_CONTENT = 'cas_content'


class Document(BaseModel):
    html: str
    language: Union[str, type(None)]


class ConnectorTermExtraction:
    """
    Connects to the Term Extraction API
    """

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
                         language: str = 'en') -> List[str]:
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

        cas = cas_from_cas_content(contact_info_response.cas_content)

        l_contact = _get_content(cas, CONTACT_PARAGRAPH_TYPE, remove_duplicate=True)

        return l_contact

    def _post_chunking(self,
                       html: str,
                       language: str = 'en'):

        doc = Document(html=html,
                       language=language
                       )

        r = requests.post(self.url + "/chunking",
                          json=doc.dict())
        j_r = r.json()

        j_r_dehyphenated = {key.replace("-", "_"): value for key, value in j_r.items()}
        chunk = ChunkModel(**j_r_dehyphenated)

        return chunk

    def _post_extract_terms(self):
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

    def _post_extract_contact_info(self,
                                   html: str,
                                   language: str = 'en') -> ContactInfo:
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

    def _post_extract_questions_answers(self):
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
