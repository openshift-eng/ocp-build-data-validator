import unittest
import flexmock

from validator.schema import image_schema


class TestImageSchema(unittest.TestCase):

    def test_validate_with_valid_data(self):
        (flexmock(image_schema.support)
            .should_receive('get_valid_streams_for')
            .and_return([]))

        (flexmock(image_schema.support)
            .should_receive('get_valid_member_references_for')
            .and_return([]))

        valid_data = {
            'from': {},
            'name': 'my-name',
        }
        self.assertIsNone(image_schema.validate('filename', valid_data))

    def test_validate_with_invalid_data(self):
        (flexmock(image_schema.support)
            .should_receive('get_valid_streams_for')
            .and_return([]))

        (flexmock(image_schema.support)
            .should_receive('get_valid_member_references_for')
            .and_return([]))

        invalid_data = {
            'from': {},
            'name': 1234,
        }
        self.assertEqual("Key 'name' error:\n1234 should be instance of 'str'",
                         image_schema.validate('filename', invalid_data))
