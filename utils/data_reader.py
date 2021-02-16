import json
from collections import namedtuple
from pathlib import Path


class Bug:

    def __init__(self, bug):

        self.bug_type = bug.get('bugType', None)
        self.fix_commit_sha1 = bug['fixCommitSHA1']
        self.fix_commit_parent_sha1 = bug['fixCommitParentSHA1']
        self.bug_file_path = bug['bugFilePath']
        self.fix_patch = bug['fixPatch']
        self.project_name = bug['projectName']
        self.bug_line_num = bug['bugLineNum']
        self.bug_node_start_char = bug['bugNodeStartChar']
        self.bug_node_length = bug['bugNodeLength']
        self.fix_line_num = bug['fixLineNum']
        self.fix_node_start_char = bug['fixNodeStartChar']
        self.fix_node_length = bug['fixNodeLength']
        self.source_before_fix = bug['sourceBeforeFix']
        self.source_after_fix = bug['sourceAfterFix']

    @property
    def username(self):
        return self.project_name.split('.')[0]

    @property
    def repository(self):
        repo_split = self.project_name.split('.')
        return '.'.join(repo_split[1:])

    @property
    def github_url(self):
        url = f'https://github.com/{self.username}/{self.repository}'
        return url

    def create_file_url(self, commit_hash):
        '''Helper method to create raw source file URLs given a specific commit'''

        url = (f'https://raw.github.com/{self.username}/{self.repository}/'
               f'{commit_hash}/{self.bug_file_path}')
        return url

    @property
    def file_url_fix_hash(self):
        return self.create_file_url(self.fix_commit_sha1)

    @property
    def file_url_parent_hash(self):
        return self.create_file_url(self.fix_commit_parent_sha1)

# TODO: Have something that returns all bug properties and something that returns all fix properties
# bug.buggy_commit, bug.fix_commit


class ManySStuBs4J:

    def __init__(self, data_path):

        with open(data_path) as data_file:
            bugs_json = json.load(data_file)

        self.bugs = [Bug(b) for b in bugs_json]

    def github_urls(self):
        return {b.github_url for b in self.bugs}


# TODO: Maybe break this into two modules and have a separate config module.
# Configuration variables start here
n_jobs = -1

# Make dataset paths relative to current module
DATASET_ROOT = Path(__file__).parent / '../data'
sstubs = DATASET_ROOT / 'sstubs.json'
bugs = DATASET_ROOT / 'bugs.json'
sstubs_large = DATASET_ROOT / 'sstubsLarge.json'
bugs_large = DATASET_ROOT / 'bugsLarge.json'

DATASET = sstubs

src_files = DATASET_ROOT / '../src_files'


def main():
    manysstubs = ManySStuBs4J(DATASET_ROOT / 'sstubs.json')
    bugs = manysstubs.bugs
    print(bugs[0].username, bugs[0].repository, bugs[0].fix_commit_sha1)
    print(bugs[0].github_url)
    print(bugs[0].file_url_fix_hash)
    print(bugs[0].file_url_parent_hash)

    print(manysstubs.github_urls())


if __name__ == '__main__':
    main()
