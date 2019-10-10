import unittest

from validator import format


class TestFormat(unittest.TestCase):

    def test_invalid_yaml(self):
        invalid_yaml = """
        key: value
        - item#1
        - item#2
        """
        (parsed, err) = format.validate(invalid_yaml)
        self.assertIsNone(parsed)
        self.assertEqual(err, "expected <block end>, but found '-'")

    def test_valid_yaml(self):
        valid_yaml = """
        key: &my_list
          - 1
          - '2'
        obj:
          lst: *my_list
        """
        (parsed, err) = format.validate(valid_yaml)
        self.assertEqual(parsed, {'key': [1, '2'], 'obj': {'lst': [1, '2']}})
        self.assertIsNone(err)
