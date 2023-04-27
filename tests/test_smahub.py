import unittest
from smahub import add_item, get_items

class TestSMAHub(unittest.TestCase):

    def setUp(self):
        self.key = 'test_key'
        self.value = 'test_value'

    def test_add_and_get_item(self):
        add_item(self.key, self.value)
        items = get_items()
        self.assertIn(self.key, items)
        self.assertEqual(items[self.key], self.value)
