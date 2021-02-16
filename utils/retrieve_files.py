import json
from pathlib import Path

import requests
from joblib import Parallel, delayed

from data_reader import DATASET, ManySStuBs4J, n_jobs


# def get_info(bug):
#     user_repo = bug['projectName'].split('.')
#     user, repo = user_repo[0], '.'.join(user_repo[1:])
#     fix_commit = bug['fixCommitSHA1']
#     fix_commit_parent = bug['fixCommitParentSHA1']
#     file_path = bug['bugFilePath']

#     return user, repo, fix_commit, fix_commit_parent, file_path


def create_url(user, repo, commit, file_path):
    '''Creating the file URL based on bug info'''

    url = f'https://raw.github.com/{user}/{repo}/{commit}/{file_path}'
    return url


def download_file(url, save_path, file_name):

    p = save_path / file_name
    if not p.exists() or p.stat().st_size == 0:
        try:
            with requests.get(url) as r:
                r.raise_for_status()
                print(url)
                save_path.mkdir(parents=True, exist_ok=True)
                with open(p, 'wb') as file:
                    file.write(r.content)
                # Check if the save file doesn't have extra new lines.
                # If yes, delete and download it again.
        except Exception as e:
            with open('error_log.txt', 'a') as logf:
                logf.write(f'{e}, {url}\n')


def main():

    manysstub = ManySStuBs4J(DATASET)
    bugs = manysstub.bugs

    output = Path('./src_files')

    parameters = []

    for bug in bugs:
        # user, repo, fix_commit, fix_commit_parent, file_path = get_info(bug)
        user, repo, fix_commit, fix_commit_parent, file_path = bug.username, bug.repository, bug.fix_commit_sha1, bug.fix_commit_parent_sha1, bug.bug_file_path
        split_path = file_path.split('/')
        save_dir = '.'.join(split_path[:-1])
        file_name = split_path[-1]

        # Downloading file with parent hash
        file_url = create_url(user, repo, fix_commit_parent, file_path)
        save_path = Path(f"{user}/{repo}/{fix_commit_parent}/{save_dir}")
        parameters.append((file_url, output / save_path, file_name))

        # Downloading file with fix hash
        file_url = create_url(user, repo, fix_commit, file_path)
        save_path = Path(f"{user}/{repo}/{fix_commit}/{save_dir}")
        parameters.append((file_url, output / save_path, file_name))

    # Parallel download
    Parallel(n_jobs=n_jobs)(delayed(download_file)(url, save_path, file_name)
                            for url, save_path, file_name in parameters)


if __name__ == '__main__':
    main()
