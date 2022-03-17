import unittest

from extract_cpsv_ap import *


class TestCLI(unittest.TestCase):
    def test_missing_args(self):
        """
        Running the CLI without any arguments
        """
        parser = get_parser()

        with self.assertRaises(SystemExit) as context:
            args = []
            args = parser.parse_args(args)

        self.assertTrue(context.exception)
        self.assertEqual(2, context.exception.code)

    def test_help(self):
        parser = get_parser()

        # Set args
        with self.assertRaises(SystemExit) as context:
            args = ["-h"]
            args = parser.parse_args(args)

        self.assertTrue(context.exception)
        self.assertEqual(0, context.exception.code)

    def test_path(self):
        """
        Simple call

        >> python .\extract_cpsv_ap.py "../data/relation_extraction/AFFLIGEM_HANDTEKENING.html"
        """

        parser = get_parser()

        # Set args
        args = ["../data/relation_extraction/AFFLIGEM_HANDTEKENING.html"]
        args = parser.parse_args(args)

        main(filename_html=args.Path)
