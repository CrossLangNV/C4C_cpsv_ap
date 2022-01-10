import base64
import os
from typing import List

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

MEDIA_ROOT = os.path.join(os.path.dirname(__file__), '../../data')
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


class CasWrapper(cassis.Cas):
    """
    wrapper around cas for our cas objects for easier extraction of content.
    """

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

    @classmethod
    def from_xmi(cls, filename):
        with open(filename, 'rb') as f:
            cas = load_cas_from_xmi(f, typesystem=TYPESYSTEM)

        return cls.from_cas(cas)

    def get_all_text(self):
        v = self.get_view(self.sofa_id)
        t = v.get_sofa().sofaString  # TODO Does get_covered_text work? Perhaps not the correct method as well
        return t

    def get_paragraphs(self) -> List[str]:
        l_par = _get_content(self, PARAGRAPH_TYPE, remove_duplicate=False)

        return l_par

    def get_contact_paragraph(self):
        """

        It could be possible that this is not available in all CAS files
        Returns:

        """

        l_contact_paragraph = _get_content(self, CONTACT_PARAGRAPH_TYPE, remove_duplicate=False)

        return l_contact_paragraph

    def get_sentences(self) -> List[str]:
        """
        Extracts all the sentences from the html.
        These are trimmed.

        Returns:
            List with sentences as strings.
        """
        l_sentence = _get_content(self, SENTENCE_TYPE)

        return l_sentence

    def _get_NER(self):
        """
        TODO test on file with NER labels

        Returns:

        """

        l_NER = _get_content(self, NER_TYPE)

        return l_NER

    def _get_question_paragraphs(self):
        """
        Paragraphs with a question in them.

        TODO test on file with questions extracted

        Returns:

        """

        return _get_content(self, QUESTION_PARAGRAPH_TYPE)

    def _get_tag(self):
        """
        TODO test if it is sometimes extracted out of a webpage.

        Returns:

        """
        return _get_content(self, TAG_TYPE)

    def _get_tokens(self):
        """

        TODO test on file with tokens

        Returns:

        """

        return _get_content(self, TOKEN_TYPE)


def _get_content(cas: cassis.Cas, annotation: str,
                 sofa_id=SOFA_ID,
                 remove_duplicate: bool = False) -> List[str]:
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

    l_annotation = []

    for ts in l_annotation_typesystem:
        s = ts.get_covered_text()
        l_annotation.append(s)

    if remove_duplicate:
        # Remove duplicates (and sorts as a consequence)
        return list(set(l_annotation))

    return l_annotation
