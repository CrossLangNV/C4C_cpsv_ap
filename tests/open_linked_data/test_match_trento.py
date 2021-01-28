"""
It is possible to use the data from Trento as an example of how the data should be exported.
For some case studies, the RDF will be compared to see if it matches the ideal output.
"""

import os
import unittest

from rdflib import Graph

from c4c_cpsv_ap.open_linked_data.terms import ConceptGraph

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))


class TestConcepts(unittest.TestCase):
    """
    Testing the construction of SKOS:Concepts
    """

    def test_simple_concepts_matching(self):

        g_reference = Graph()
        g_reference.parse(os.path.join(ROOT, 'examples/data/trento.jsonld'), format='json-ld')

        id = 'http://cpsvap.semic.eu/Q88.9.9'
        label = "Q88.9.9 - Other social work activities without accommodation n.e.c."

        g = ConceptGraph()

        g.add_terms_with_uri({id: label}, lang='en')

        for triple in g:

            s, p, o = triple

            with self.subTest(triple):

                # Find matching subjects
                triples_matching_obj = list(filter(lambda t: str(t[-1]) == str(o), g_reference))

                if not len(triples_matching_obj):
                    self.fail(f"Couldn't find the object: {o}")

                triples_matching_pred_obj = list(filter(lambda t: str(t[1]) == str(p), triples_matching_obj))

                if not len(triples_matching_pred_obj):
                    self.fail(f"Couldn't find a matching predicate-subject: {p}")

                triples_matching = list(filter(lambda t: str(t[0]) == str(s), triples_matching_pred_obj))

                if not len(triples_matching):
                    self.fail(f"Couldn't find a matching subject-predicate-object: {s}")
