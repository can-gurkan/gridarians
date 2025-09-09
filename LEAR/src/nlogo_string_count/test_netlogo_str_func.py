import unittest
from netlogo_str_func import netlogo_length

class TestNetLogoLength(unittest.TestCase):

    def setUp(self):
        self.sample_code = """
        to go
          ; this is a comment
          if count turtles > 0 [
            fd 1 ; move forward
          ]
        end
        """

    def test_chars_no_comments(self):
        result = netlogo_length(self.sample_code)
        self.assertEqual(result, 28)

    def test_chars_with_comments(self):
        result = netlogo_length(self.sample_code, remove_comments=False)
        self.assertEqual(result, 55)

    def test_words_no_comments(self):
        result = netlogo_length(self.sample_code, count_words=True)
        self.assertEqual(result, 12)

    def test_words_with_comments(self):
        result = netlogo_length(self.sample_code, remove_comments=False, count_words=True)
        self.assertEqual(result, 20)

if __name__ == '__main__':
    unittest.main()