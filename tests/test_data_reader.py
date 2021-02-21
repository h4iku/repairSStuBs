import unittest
from pathlib import Path

from utils.data_reader import ManySStuBs4J


class TestDataReader(unittest.TestCase):

    def setUp(self):
        FIXS_ROOT = Path(__file__).parent / 'fixtures'
        manysstubs = ManySStuBs4J(FIXS_ROOT / 'sstub.json')
        self.bug = manysstubs.bugs[0]

    def test_bug_type(self):
        self.assertEqual(self.bug.bug_type, 'CHANGE_NUMERAL')

    def test_fix_commit_sha1(self):
        result = '697a5ff366eccf069fa933a25323839a8aa4abd2'
        self.assertEqual(self.bug.fix_commit_sha1, result)

    def test_fix_commit_parent_sha1(self):
        result = '9d86c3b12fdbb4a8e0110f40e5abb460645b9a01'
        self.assertEqual(self.bug.fix_commit_parent_sha1, result)

    def test_username(self):
        self.assertEqual(self.bug.username, 'apache')

    def test_repository(self):
        self.assertEqual(self.bug.repository, 'camel.github.io')

    def test_github_url(self):
        result = 'https://github.com/apache/camel.github.io'
        self.assertEqual(self.bug.github_url, result)

    def test_file_url_fix_hash(self):
        result = (
            'https://raw.github.com/apache/camel.github.io/'
            '697a5ff366eccf069fa933a25323839a8aa4abd2/'
            'camel-core/src/test/java/org/apache/camel/component/file/FileConsumerBeginAndCommitRenameStrategyTest.java'
        )
        self.assertEqual(self.bug.file_url_fix_hash, result)

    def test_file_url_parent_hash(self):
        result = (
            'https://raw.github.com/apache/camel.github.io/'
            '9d86c3b12fdbb4a8e0110f40e5abb460645b9a01/'
            'camel-core/src/test/java/org/apache/camel/component/file/FileConsumerBeginAndCommitRenameStrategyTest.java'
        )
        self.assertEqual(self.bug.file_url_parent_hash, result)

    def test_file_name(self):
        result = 'FileConsumerBeginAndCommitRenameStrategyTest.java'
        self.assertEqual(self.bug.file_name, result)

    def test_file_dir(self):
        result = 'camel-core.src.test.java.org.apache.camel.component.file'
        self.assertEqual(self.bug.file_dir, result)

    def test_buggy_file_dir(self):
        result = Path(
            'apache.camel.github.io/'
            '9d86c3b12fdbb4a8e0110f40e5abb460645b9a01/'
            'camel-core.src.test.java.org.apache.camel.component.file'
        )
        self.assertEqual(self.bug.buggy_file_dir, result)

    def test_fixed_file_dir(self):
        result = Path(
            'apache.camel.github.io/'
            '697a5ff366eccf069fa933a25323839a8aa4abd2/'
            'camel-core.src.test.java.org.apache.camel.component.file'
        )
        self.assertEqual(self.bug.fixed_file_dir, result)

    def test_buggy_file_line_dir(self):
        result = Path(
            'apache.camel.github.io/'
            '9d86c3b12fdbb4a8e0110f40e5abb460645b9a01/'
            'camel-core.src.test.java.org.apache.camel.component.file/'
            'FileConsumerBeginAndCommitRenameStrategyTest.java/'
            '51'
        )
        self.assertEqual(self.bug.buggy_file_line_dir, result)

    def test_fixed_file_line_dir(self):
        result = Path(
            'apache.camel.github.io/'
            '697a5ff366eccf069fa933a25323839a8aa4abd2/'
            'camel-core.src.test.java.org.apache.camel.component.file/'
            'FileConsumerBeginAndCommitRenameStrategyTest.java/'
            '52'
        )
        self.assertEqual(self.bug.fixed_file_line_dir, result)


if __name__ == '__main__':
    unittest.main()
