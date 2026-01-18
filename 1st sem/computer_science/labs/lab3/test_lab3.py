import unittest
import lab3


class TestTask1(unittest.TestCase):
    def test_no_emotions(self):
        data = 'happines is only a capcake away'
        result = 0
        self.assertEqual(result, lab3.solve(data))

    def test_breaked_emotions(self):
        data = 'hot chocolate is like a hug from the inside [< ) ;< ) :<0 [<) ; <) ;<)'
        result = 1
        self.assertEqual(result, lab3.solve(data))

    def test_one_emotion(self):
        data = '[<)'
        result = 1
        self.assertEqual(result, lab3.solve(data))

    def test_many_emotions(self):
        data = '[<)[<)[<)[<)[<)[<)'
        result = 6
        self.assertEqual(result, lab3.solve(data))

    def test_emotions_with_splits(self):
        data = '[][<) the day [[[<)))   you plant the seed    [<)-[<)-[<)-[<)) is not the day you eat the fruit :))[<*)'
        result = 6
        self.assertEqual(result, lab3.solve(data))


if __name__ == '__main__':
    unittest.main()