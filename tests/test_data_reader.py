import unittest
from pathlib import Path

from utils.data_reader import ManySStuBs4J


class TestDataReader(unittest.TestCase):

    FIXS_ROOT = Path(__file__).parent / 'fixtures'
    manysstubs = ManySStuBs4J(FIXS_ROOT / 'sstub.json')
    bug = manysstubs.bugs[0]

    def test_bug_type(self):
        self.assertEqual(TestDataReader.bug.bug_type, 'CHANGE_NUMERAL')


if __name__ == '__main__':
    unittest.main()
