from relation_extraction.nova_gorica import NovaGoricaParser


class ZagrebParser(NovaGoricaParser):
    """
    Use AalterParser or AffligemParser
    """

    criterionRequirement = r"(?=x)(?!x)"  # TODO, not implemented
    rule = r"(?=x)(?!x)"  # TODO, not implemented
    evidence = r"(?=x)(?!x)"  # TODO, not implemented
    cost = r"(?=x)(?!x)"  # TODO, not implemented
