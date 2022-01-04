import base64
import os

from cassis import load_cas_from_xmi, load_typesystem

CONTACT_PARAGRAPH_TYPE = "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.ContactParagraph"
SOFA_ID = "html2textView"

MEDIA_ROOT = os.path.join(os.path.dirname(__file__), '../data')
with open(os.path.join(MEDIA_ROOT, 'typesystem.xml'), 'rb') as f:
    TYPESYSTEM = load_typesystem(f)


def cas_from_cas_content(cas_content: str):
    """

    Args:
        cas_content: The encoded UIMA CASSIS as string.

    Returns:
        deserialized cassis.CAS object
    """
    decoded_cas_content = get_decoded_cas_content(cas_content)

    cas = load_cas_from_xmi(decoded_cas_content,
                            typesystem=TYPESYSTEM,
                            trusted=True)

    return cas


def get_decoded_cas_content(cas_content: str):
    return base64.b64decode(cas_content).decode('utf-8')