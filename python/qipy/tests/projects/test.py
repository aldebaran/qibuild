import unittest
import eggs

class OverloadTest(unittest.TestCase):
    """Test that eggs method in C++ are correctly wrapped

    """
    def test_eggs(self):
        """Call foo() and foo(43) """
        self.assertEqual(eggs.foo(),   42)
        self.assertEqual(eggs.foo(43), 43)

    def test_defaul_args(self):
        self.assertEqual(eggs.bar(), 42)
        self.assertEqual(eggs.bar(43), 43)


if __name__ == "__main__":
    unittest.main()
