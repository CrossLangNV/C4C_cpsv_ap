from relation_extraction.cities import ClassifierCityParser, RegexCPSVAPRelationsClassifier


class AalterCPSVAPRelationsClassifier(RegexCPSVAPRelationsClassifier):
    """
    For https://www.aalter.be/
    """

    def __init__(self,
                 pattern_criterion_requirement=r"voorwaarden(.)*",
                 pattern_rule=r"hoe(.)*",
                 pattern_evidence=r"wat meebrengen(.)*",  # with or without ?
                 pattern_cost=r"prijs(.)*",
                 ):
        super(AalterCPSVAPRelationsClassifier, self).__init__(
            pattern_criterion_requirement=pattern_criterion_requirement,
            pattern_rule=pattern_rule,
            pattern_evidence=pattern_evidence,
            pattern_cost=pattern_cost
        )


class AalterParser(ClassifierCityParser):
    """
    Parser for Aalter.be
    """

    def __init__(self, classifier: AalterCPSVAPRelationsClassifier = None):
        if classifier is None:
            # Default behaviour
            classifier = AalterCPSVAPRelationsClassifier()

        super(AalterParser, self).__init__(classifier)
