import unittest

from fixture_magic.utils import reorder_json, get_fields, get_m2m

from .models import Person, Group

__author__ = 'davedash'


class UtilsTestCase(unittest.TestCase):
    def test_reorder_json(self):
        """Test basic ordering of JSON/python object."""
        input_json = [{'model': 'f'}, {'model': 'x'},]
        expected = [{'model': 'x'}, {'model': 'f'}]
        self.assertEqual(expected, reorder_json(input_json, models=['x', 'f'])
        )

    def test_get_fields(self):
        fields = get_fields(Person)
        field_names = [field.name for field in fields]
        self.assertIn("first_name", field_names)

    def test_get_fields_exclude(self):
        fields = get_fields(Person, "last_name")
        field_names = [field.name for field in fields]
        self.assertIn("first_name", field_names)
        self.assertNotIn("last_name", field_names)

    def test_get_m2m(self):
        fields = get_m2m(Group)
        field_names = [field.name for field in fields]
        self.assertIn("members", field_names)
