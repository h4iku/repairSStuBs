import requests
from joblib import Parallel, delayed

from data_reader import DATASET, SRC_FILES, ManySStuBs4J, n_jobs


def check_extra_newline(jfile):
    '''Sometimes downloaded files have extra new lines in each line.
    This function detects and deletes these extra new lines.
    '''

    with open(jfile, 'rb') as jf:
        content = jf.read()

    lines = content.splitlines()
    odd_lines = lines[1::2]
    if all((x == b'' for x in odd_lines)):
        print(jfile)
        with open(jfile, 'wb') as f:
            f.write(b'\n'.join(lines[::2]))


def download_file(url, save_path):

    while not save_path.exists() or save_path.stat().st_size == 0:
        try:
            with requests.get(url) as r:
                r.raise_for_status()
                save_path.parent.mkdir(parents=True, exist_ok=True)
                with open(save_path, 'wb') as file:
                    file.write(r.content)
        except Exception as e:
            with open('error_log.txt', 'a') as logf:
                logf.write(f'{e}, {url}\n')

    check_extra_newline(save_path)


def main():

    manysstub = ManySStuBs4J(DATASET)

    download_params = []

    for bug in manysstub.bugs:

        # Downloading file with parent hash
        download_params.append(
            (bug.file_url_parent_hash,
             SRC_FILES / bug.buggy_file_dir / bug.file_name)
        )

        # Downloading file with fix hash
        download_params.append(
            (bug.file_url_fix_hash,
             SRC_FILES / bug.fixed_file_dir / bug.file_name)
        )

    # Parallel download
    Parallel(n_jobs=n_jobs)(delayed(download_file)(url, save_path)
                            for url, save_path in download_params)


if __name__ == '__main__':
    main()
