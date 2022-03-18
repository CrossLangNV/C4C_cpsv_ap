import unittest

from extract_cpsv_ap import *


class TestCLI(unittest.TestCase):
    def test_1_missing_args(self):
        """
        Running the CLI without any arguments
        """
        parser = get_parser()

        # Command
        l_args = []
        self.print_command(l_args)

        with self.assertRaises(SystemExit) as context:
            args = parser.parse_args(l_args)

        self.assertTrue(context.exception)
        self.assertEqual(2, context.exception.code)

    def test_2_help(self):
        parser = get_parser()

        # Command
        l_args = ["-h"]
        self.print_command(l_args)

        # Set args
        with self.assertRaises(SystemExit) as context:
            args = parser.parse_args(l_args)

        self.assertTrue(context.exception)
        self.assertEqual(0, context.exception.code)

    def test_3_path(self):
        """
        Simple call

        >> python .\extract_cpsv_ap.py "../data/relation_extraction/AFFLIGEM_HANDTEKENING.html"
        """

        parser = get_parser()

        # Set args
        l_args = ["../data/relation_extraction/AFFLIGEM_HANDTEKENING.html",
                  "DEMO_AFFLIGEM.rdf"]
        args = parser.parse_args(l_args)

        # Command
        self.print_command(l_args)

        main(filename_html=args.Path,
             filename_rdf=args.RDF,
             extract_concepts=args.concepts)

    def test_4_concept_extraction(self):
        """
        """

        parser = get_parser()

        # Set args
        l_args = ["--concepts",
                  "../data/relation_extraction/AFFLIGEM_HANDTEKENING.html",
                  "DEMO_AFFLIGEM_CONCEPTS.rdf"
                  ]
        # Command
        self.print_command(l_args)

        args = parser.parse_args(l_args)

        main(filename_html=args.Path,
             filename_rdf=args.RDF,
             extract_concepts=args.concepts)

    def test_5_norway(self):
        parser = get_parser()

        # Set args
        l_args = [
            "../tests/relation_extraction/EXAMPLE_FILES/https_austrheim_kommune_no_innhald_helse_sosial_og_omsorg_pleie_og_omsorg_omsorgsbustader_.html",
            "DEMO_AUSTRHEIM.rdf"
            ]
        # Command
        self.print_command(l_args)

        args = parser.parse_args(l_args)

        main(filename_html=args.Path,
             filename_rdf=args.RDF,
             extract_concepts=args.concepts,
             context="austrheim.kommune.no",  # TODO add flags
             country_code="NO",  # TODO add flags
             url="https://austrheim.kommune.no/innhald/helse-sosial-og-omsorg/pleie-og-omsorg/omsorgsbustader/")

    @staticmethod
    def print_command(l_args):
        print()
        print("$ python extract_cpsv_ap.py", *l_args)
        print()


class TestCLIBreaking(unittest.TestCase):
    """Testing out edge cases"""

    def setUp(self) -> None:
        self.RDF_DEBUG = "DEMO_AFFLIGEM_DEBUG.rdf"

    def test_could_not_find_html(self):
        parser = get_parser()

        # Set args
        args = ["../data/relation_extraction/THIS_FILE_SHOULD_NOT_EXISTS.html",
                self.RDF_DEBUG]

        args = parser.parse_args(args)

        with self.assertRaises(FileNotFoundError) as context:
            main(filename_html=args.Path,
                 filename_rdf=args.RDF)

        self.assertTrue(context.exception)
