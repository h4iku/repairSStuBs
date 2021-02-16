from pathlib import Path

import requests
from joblib import Parallel, delayed

from data_reader import DATASET, ManySStuBs4J, n_jobs


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

    output = Path('./src_files')

    download_params = []

    for bug in manysstub.bugs:

        # Downloading file with parent hash
        download_params.append(
            (bug.file_url_parent_hash,
             output / bug.buggy_file_dir,
             bug.file_name)
        )

        # Downloading file with fix hash
        download_params.append(
            (bug.file_url_fix_hash,
             output / bug.fixed_file_dir,
             bug.file_name)
        )

    # Parallel download
    Parallel(n_jobs=n_jobs)(delayed(download_file)(url, save_path, file_name)
                            for url, save_path, file_name in download_params)


if __name__ == '__main__':
    main()
