import unittest
from threading import Thread
from time import sleep
from smadict import SMA_Dict

class TestSmaDict(unittest.TestCase):
    def test_basic_operations(self):
        d = SMA_Dict()
        d['a'] = 1
        d['b'] = 2
        d['c'] = 3
        self.assertEqual(d['a'], 1)
        self.assertEqual(d['b'], 2)
        self.assertEqual(d['c'], 3)
        del d['b']
        self.assertNotIn('b', d)

    def test_iteration(self):
        d = SMA_Dict(a=1, b=2, c=3)
        keys = set()
        for k in d:
            keys.add(k)
        self.assertEqual(keys, {'a', 'b', 'c'})

    def test_length(self):
        d = SMA_Dict(a=1, b=2, c=3)
        self.assertEqual(len(d), 3)
        d['d'] = 4
        self.assertEqual(len(d), 4)

    def test_callback(self):
        d = SMA_Dict()
        def callback(key, value):
            self.assertEqual(key, 'a')
            self.assertEqual(value, 1)
        d.register_callback(callback)
        d['a'] = 1

        # Wait a bit to ensure that the callback is called
        sleep(0.1)

    def test_copy_method(self):
        original_dict = SMA_Dict({'a': 1, 'b': 2, 'c': 3})
        copied_dict = original_dict.__copy__()

        # Check that the copied dict is a separate object
        self.assertIsNot(copied_dict, original_dict)

        # Check that the copied dict has the same items
        self.assertEqual(copied_dict, original_dict)

        # Check that modifying the copied dict doesn't affect the original dict
        copied_dict['a'] = 10
        self.assertNotEqual(copied_dict['a'], original_dict['a'])
        self.assertEqual(copied_dict['b'], original_dict['b'])
        self.assertEqual(copied_dict['c'], original_dict['c'])

if __name__ == '__main__':
    unittest.main()
