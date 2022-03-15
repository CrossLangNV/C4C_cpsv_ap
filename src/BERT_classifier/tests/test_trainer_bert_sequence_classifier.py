import unittest

from bert_based_classifier.trainer_bert_sequence_classifier import TrainerBertSequenceClassifier


class MyTestCase(unittest.TestCase):
    def test_something(self):
        classifier = TrainerBertSequenceClassifier()

        self.assertEqual(True, False)  # add assertion here


if __name__ == '__main__':
    unittest.main()
