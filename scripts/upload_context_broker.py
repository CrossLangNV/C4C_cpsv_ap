import argparse

from context_broker.context_broker_connector import get_jsonld, upload_jsonld_to_orion


def get_parser():
    parser = argparse.ArgumentParser(prog="upload_context_broker",
                                     description='Upload the content of an RDF to the Context Broker')

    # Add the arguments
    parser.add_argument('rdf',
                        metavar='file',
                        type=str,
                        help='input filename to read the RDF')

    return parser


def upload_rdf_to_context_broker(filename: str):
    """
    Uploads the content of the RDF to the Orion Context Broker.

    Args:
        filename: Filename to the RDF.

    Returns:

    """

    jsonld = get_jsonld(filename=filename)

    upload_jsonld_to_orion(jsonld)

    return 0


def main(args: argparse.Namespace):
    """
    Runs the method from the command line interface.

    Args:
        args: As defined in get_parser()

    Returns:

    """
    return upload_rdf_to_context_broker(filename=args.rdf)


if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()

    main(args)
