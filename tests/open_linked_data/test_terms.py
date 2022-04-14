import os
import tempfile
import unittest

import pandas as pd

from c4c_cpsv_ap.open_linked_data.terms import ConceptGraph

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))

FILENAME_WIEN_PROCEDURES_VOC = os.path.join(ROOT, 'examples/data/wien-procedures-voc.csv')
KEY_TERMS = 'terms'


class TestTerms(unittest.TestCase):
    def test_rdf_and_export(self):
        df = pd.read_csv(FILENAME_WIEN_PROCEDURES_VOC,
                         delimiter=','
                         )

        l_terms = list(df.get(KEY_TERMS))

        g = ConceptGraph()

        g.add_terms(l_terms, lang='de')

        with tempfile.TemporaryDirectory() as tmp_dir:
            outputs = ['xml', 'turtle']

            for format in outputs:
                with self.subTest(format):
                    g.serialize(destination=os.path.join(tmp_dir, f'output.{format}'), format=format)

        return df
