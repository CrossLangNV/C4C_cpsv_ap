from relation_extraction.aalter import AalterParser


class WienParser(AalterParser):
    """
    Use AalterParser or AffligemParser
    """

    criterionRequirement = r"voraussetzungen(.)*"
    rule = r"allgemeine informationen(.)*"
    evidence = r"erforderliche unterlagen(.)*"
    cost = r"kosten(.)*"
