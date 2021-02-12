import json


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
    def github_link(self):
        pass

# TODO: Have something that returns all bug properties and something that returns all fix properties
# bug.buggy_commit, bug.fix_commit

# TODO: Maybe name the module `manysstubs_reader` or `dataset_reader` and name the function `get_data`


def get_bugs(data_path):

    with open(data_path) as data_file:
        bugs_json = json.load(data_file)

    bugs = [Bug(b) for b in bugs_json]
    # print(bugs[0].username, bugs[0].repository, bugs[0].fix_commit_sha1)

    return bugs


if __name__ == '__main__':
    get_bugs('../_data/sstubs.json')
