from relation_extraction.cities import CityParser
from relation_extraction.methods import RelationExtractor


class RelationExtractor2(RelationExtractor):
    """
    The extended version of RelationExtractor

    TODO
     * Move the whole class to this module.
    """

    def __init__(self, *args, parser: CityParser, **kwargs):
        super(RelationExtractor2, self).__init__(*args, **kwargs)

        self.parser = parser

    def extract_all(self, *args, **kwargs):
        super(RelationExtractor2, self).extract_all(*args, **kwargs)
