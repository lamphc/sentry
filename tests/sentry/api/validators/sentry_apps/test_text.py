from __future__ import absolute_import

from sentry.testutils import TestCase

from .util import invalid_schema, validate_component


class TestTextSchemaValidation(TestCase):
    def setUp(self):
        self.schema = {
            'type': 'text',
            'name': 'title',
            'label': 'Title',
        }

    def test_valid_schema(self):
        validate_component(self.schema)

    @invalid_schema
    def test_missing_name(self):
        del self.schema['name']
        validate_component(self.schema)

    @invalid_schema
    def test_missing_label(self):
        del self.schema['label']
        validate_component(self.schema)

    @invalid_schema
    def test_invalid_label_type(self):
        self.schema['label'] = 1
        validate_component(self.schema)

    @invalid_schema
    def test_invalid_name_type(self):
        self.schema['name'] = 1
        validate_component(self.schema)
