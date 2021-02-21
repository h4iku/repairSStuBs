import requests
from joblib import Parallel, delayed
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .data_reader import DATASET, SRC_FILES, ManySStuBs4J, n_jobs


def download_file(session, url, save_path):

    if not save_path.exists() or save_path.stat().st_size == 0:
        try:
            with session.get(url) as r:
                r.raise_for_status()
                save_path.parent.mkdir(parents=True, exist_ok=True)
                with open(save_path, 'wb') as file:
                    file.write(r.content)
        except Exception as e:
            with open('error_log.txt', 'a') as logf:
                logf.write(f'{e}, {url}\n')


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

    with requests.Session() as session:
        retries = Retry(total=5,
                        backoff_factor=0.1,
                        status_forcelist=[500, 502, 503, 504])
        session.mount('https://', HTTPAdapter(max_retries=retries))

        Parallel(n_jobs=n_jobs)(delayed(download_file)(session, url, save_path)
                                for url, save_path in download_params)


if __name__ == '__main__':
    main()
