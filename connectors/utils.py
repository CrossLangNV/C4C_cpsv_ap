import base64
import os

import cassis
from cassis import load_cas_from_xmi, load_typesystem

# [Annotation]
TAG_TYPE = "com.crosslang.uimahtmltotext.uima.type.ValueBetweenTagType"
SOFA_ID = "html2textView"
SENTENCE_TYPE = "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence"
PARAGRAPH_TYPE = "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Paragraph"
CONTACT_PARAGRAPH_TYPE = "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.ContactParagraph"
QUESTION_PARAGRAPH_TYPE = "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.QuestionParagraph"
TOKEN_TYPE = "cassis.Token"
NER_TYPE = "de.tudarmstadt.ukp.dkpro.core.api.ner.type.NamedEntity"

MEDIA_ROOT = os.path.join(os.path.dirname(__file__), '../data')
with open(os.path.join(MEDIA_ROOT, 'typesystem.xml'), 'rb') as f:
    TYPESYSTEM = load_typesystem(f)


def cas_from_cas_content(cas_content: str) -> cassis.Cas:
    """

    Args:
        cas_content: The encoded UIMA CASSIS as string.

    Returns:
        deserialized cassis.CAS object
    """
    decoded_cas_content = get_decoded_cas_content(cas_content)

    cas = load_cas_from_xmi(decoded_cas_content,
                            typesystem=TYPESYSTEM,
                            # trusted=True # TODO fix "TypeError: load_cas_from_xmi() got an unexpected keyword argument 'trusted'"
                            )

    return cas


def get_decoded_cas_content(cas_content: str):
    return base64.b64decode(cas_content).decode('utf-8')


class CasChunk(cassis.Cas):

    def __init__(self,
                 *args,
                 sofa_id=SOFA_ID,
                 **kwargs,
                 ):
        super().__init__(*args, **kwargs)

        self.sofa_id = sofa_id

    @classmethod
    def from_cas_content(cls, cas_content: str):
        return cls.from_cas(cas_from_cas_content(cas_content))

    @classmethod
    def from_cas(cls, cas: cassis.Cas):
        """
        Make a copy of a cassis.Cas object to this class .
        based on https://stackoverflow.com/questions/60920784/python-how-to-convert-an-existing-parent-class-object-to-child-class-object

        Args:
            cas:

        Returns:

        """
        _self = cls(typesystem=cas.typesystem,
                    lenient=cas._lenient)

        _self.__dict__.update(cas.__dict__)

        return _self

    def get_all_text(self):
        v = self.get_view(self.sofa_id)
        t = v.get_sofa().sofaString
        return t
