import unittest

from connectors.term_extraction_utils.models import ChunkModel
# Example of chunking response
from connectors.utils import CasChunk

J_R = {'title': 'Financial plan: how to prepare an effective financial plan', 'tags': '',
       'excerpt': 'The financial plan is a dynamic instrument and an essential management tool. What should it include? Who can help?',
       'text': '1819 is a service from hub.brussels, the Brussels agency for business support. 1819 is a platform and a single information point for anyone who wants to start, grow or develop a business in Brussels in a professional manner and who is looking for information and help to do so. We put you on the right track, guide you quickly through all the information and direct you to the partners who can help you to make your project a real success, all free of charge!',
       'hostname': '1819.brussels', 'source-hostname': '1819.brussels',
       'source': 'https://1819.brussels/en/information-library/start-business-formalities/financial-plan',
       'language': 'en',
       'cas_content': 'PD94bWwgdmVyc2lvbj0nMS4wJyBlbmNvZGluZz0nQVNDSUknPz4KPHhtaTpYTUkgeG1sbnM6eG1pPSJodHRwOi8vd3d3Lm9tZy5vcmcvWE1JIiB4bWxuczpjYXM9Imh0dHA6Ly8vdWltYS9jYXMuZWNvcmUiIHhtbG5zOnR5cGU9Imh0dHA6Ly8vZGUvdHVkYXJtc3RhZHQvdWtwL2RrcHJvL2NvcmUvYXBpL3NlZ21lbnRhdGlvbi90eXBlLmVjb3JlIiB4bWk6dmVyc2lvbj0iMi4wIj48Y2FzOk5VTEwgeG1pOmlkPSIwIi8+PHR5cGU6U2VudGVuY2UgeG1pOmlkPSIzIiBpZD0icmVndWxhciBzZW50ZW5jZSIgYmVnaW49IjAiIGVuZD0iNDU5IiBzb2ZhPSIyIi8+PGNhczpTb2ZhIHhtaTppZD0iMSIgc29mYU51bT0iMSIgc29mYUlEPSJfSW5pdGlhbFZpZXciIG1pbWVUeXBlPSJOb25lIiBzb2ZhU3RyaW5nPSJOb25lIi8+PGNhczpTb2ZhIHhtaTppZD0iMiIgc29mYU51bT0iMiIgc29mYUlEPSJodG1sMnRleHRWaWV3IiBtaW1lVHlwZT0iTm9uZSIgc29mYVN0cmluZz0iMTgxOSBpcyBhIHNlcnZpY2UgZnJvbSBodWIuYnJ1c3NlbHMsIHRoZSBCcnVzc2VscyBhZ2VuY3kgZm9yIGJ1c2luZXNzIHN1cHBvcnQuIDE4MTkgaXMgYSBwbGF0Zm9ybSBhbmQgYSBzaW5nbGUgaW5mb3JtYXRpb24gcG9pbnQgZm9yIGFueW9uZSB3aG8gd2FudHMgdG8gc3RhcnQsIGdyb3cgb3IgZGV2ZWxvcCBhIGJ1c2luZXNzIGluIEJydXNzZWxzIGluIGEgcHJvZmVzc2lvbmFsIG1hbm5lciBhbmQgd2hvIGlzIGxvb2tpbmcgZm9yIGluZm9ybWF0aW9uIGFuZCBoZWxwIHRvIGRvIHNvLiBXZSBwdXQgeW91IG9uIHRoZSByaWdodCB0cmFjaywgZ3VpZGUgeW91IHF1aWNrbHkgdGhyb3VnaCBhbGwgdGhlIGluZm9ybWF0aW9uIGFuZCBkaXJlY3QgeW91IHRvIHRoZSBwYXJ0bmVycyB3aG8gY2FuIGhlbHAgeW91IHRvIG1ha2UgeW91ciBwcm9qZWN0IGEgcmVhbCBzdWNjZXNzLCBhbGwgZnJlZSBvZiBjaGFyZ2UhIi8+PGNhczpWaWV3IHNvZmE9IjEiIG1lbWJlcnM9IiIvPjxjYXM6VmlldyBzb2ZhPSIyIiBtZW1iZXJzPSIzIi8+PC94bWk6WE1JPg=='}
J_R_Dehyphen = {key.replace("-", "_"): value for key, value in J_R.items()}


class TestChunkModel(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def test_init(self):
        chunk = ChunkModel(**J_R_Dehyphen)

        with self.subTest("title"):
            self.assertTrue(chunk.title, "Expected a title")

        with self.subTest("excerpt"):
            self.assertTrue(chunk.excerpt, "Expected a excerpt")

        with self.subTest("text"):
            self.assertTrue(chunk.text, "Expected a text")

        with self.subTest("cas"):
            self.assertTrue(chunk.title, "Expected a title")

        with self.subTest("title"):
            self.assertTrue(chunk.title, "Expected a title")
        with self.subTest("title"):
            self.assertTrue(chunk.title, "Expected a title")

    def test_cas(self):
        chunk = ChunkModel(**J_R_Dehyphen)

        cas_chunk = CasChunk.from_cas_content(chunk.cas_content)

        t = cas_chunk.get_all_text()

        self.assertEqual(chunk.text,
                         t)
