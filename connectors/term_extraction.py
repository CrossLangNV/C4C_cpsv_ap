import warnings
from typing import List

import cassis
import requests

from connectors.term_extraction_utils.models import ChunkModel
from connectors.utils import cas_from_cas_content, CONTACT_PARAGRAPH_TYPE, SOFA_ID

KEY_CAS_CONTENT = 'cas_content'


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

    def post_chunking(self,
                      html: str,
                      language: str = 'en'):

        j = {
            "html": html,
            "language": language
        }

        r = requests.post(self.url + "/chunking",
                          json=j)
        j_r = r.json()

        j_r_dehyphenated = {key.replace("-", "_"): value for key, value in j_r.items()}
        chunk = ChunkModel(**j_r_dehyphenated)

        return chunk

    def post_contact_info(self,
                          html: str,
                          language: str = 'en') -> List[str]:
        """
        Extracts the contact info from a webpage.

        Args:
            html: HTML of a webpage, classified as containing a public service procedure.
            language:
                en, fr, de...

        Returns:
            contact info, saved in a CAS object.
        """

        j = {
            "html": html,
            "language": language
        }

        r = requests.post(self.url + "/extract_contact_info",
                          json=j)
        j_r = r.json()

        cas = cas_from_cas_content(j_r[KEY_CAS_CONTENT])

        l_contact = _get_content(cas, CONTACT_PARAGRAPH_TYPE)

        return l_contact


class ConnectionWarning(Warning):
    """
    Custom warning when the connection might be lost.
    """


def _get_content(cas: cassis.Cas, annotation: str,
                 sofa_id=SOFA_ID) -> List[str]:
    """
    Returns list of annotated objects within the CAS.

    Args:
        cas:
        annotation: (str) annotation found in cas object.
        sofa_id: uses default SOFA_ID.

    Returns:

    """
    l_annotation_typesystem = cas.get_view(sofa_id).select(annotation)

    """
    [TYPESYSTEM.get_type(CONTACT_PARAGRAPH_TYPE)]
    l_contact_typesystem[0].content_context
    l_contact_typesystem[0].content
    """

    l_annotation = list(set(map(lambda ts: ts.content, l_annotation_typesystem)))

    return l_annotation
