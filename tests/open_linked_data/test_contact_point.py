import os
import tempfile
import unittest

from c4c_cpsv_ap.open_linked_data.contact_point import ContactPoint, ContactPointGraph


class TestContactPoint(unittest.TestCase):
    def test_construction(self):
        cp = ContactPoint()
        cp.add_email('abc@def.ghi')
        cp.add_email('abc@def.ghi')  # TODO Duplicates should not removed in RDF
        cp.add_telephone('++0123456')

        cp2 = ContactPoint(email='The adress\nThis is my adress\ncba\n @ \n  mail.io')

        l_cp = [cp, cp2]

        g = ContactPointGraph()

        with self.subTest('Export'):
            with tempfile.TemporaryDirectory() as tmp_dir:
                for cp_i in l_cp:
                    g.add_contact_point(cp_i)

                g.serialize(destination=os.path.join(tmp_dir, f'test_contact_points.rdf'))
