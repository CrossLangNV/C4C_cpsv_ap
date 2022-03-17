import argparse
import os.path
import warnings


def get_parser():
    parser = argparse.ArgumentParser(description='Extract the adminstrative procedure ontology out of a html page,'
                                                 ' as defined by the CPSV-AP vocabulary.')

    # Add the arguments
    parser.add_argument('Path',
                        metavar='path',
                        type=str,
                        help='the path to HTML')

    return parser


def main(filename_html):
    """
    Extract

    Input
        - HTML
    Output
        - RDF (based on CPSV-AP)

    Returns:

    """

    if not os.path.exists(filename_html):
        warnings.warn(f"Could not find {filename_html}", UserWarning)

    print("Hello World")
    return


if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()

    main(filename_html=args.Path)
