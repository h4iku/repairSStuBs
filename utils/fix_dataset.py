import json

import requests
from joblib import Parallel, delayed

from .config import DATASET, n_jobs
from .data_reader import ManySStuBs4J


def replace_project_names(data):
    '''Replacing project names for projects that are deleted from GitHub
    or their project name only contains the repository part.
    '''

    # Deleted and forked ones
    deleted_projects = {
        'AndroidBootstrap.android-bootstrap': 'a-thomas.android-bootstrap',
        'wyouflf.xUtils': 'lailiaomm.xUtils',
        'floragunncom.search-guard': 'ballesterosam.search-guard',
        'b3log.solo': '88250.solo',
        'b3log.symphony': '88250.symphony',
        'jersey.jersey': 'javaee.jersey'
    }

    # Without user part, with only repository name
    repo_only_projects = {
        'bazel': 'bazelbuild.bazel',
        'netty-in-action': 'normanmaurer.netty-in-action',
        'Intro-To-RxJava': 'Froussios.Intro-To-RxJava',
        'struts': 'apache.struts',
        'killbill': 'killbill.killbill',
        'spring-integration': 'spring-projects.spring-integration',
        'spydroid-ipcamera': 'fyhertz.spydroid-ipcamera',
        'failsafe': 'jhalterman.failsafe',
        'focus-android': 'mozilla-mobile.focus-android',
        'libnd4j': 'deeplearning4j.libnd4j'
    }

    project_names = {**deleted_projects, **repo_only_projects}

    for bug in data:
        if bug['projectName'] in project_names:
            bug['projectName'] = project_names[bug['projectName']]

    return data


def check_projects():
    '''Checks if all projects are available on GitHub'''

    manysstubs = ManySStuBs4J(DATASET)
    try:
        Parallel(n_jobs=n_jobs)(delayed(lambda url: requests.get(url).raise_for_status())(url)
                                for url in manysstubs.github_urls())
    except requests.exceptions.RequestException as e:
        print(e)


def main():

    with open(DATASET) as file:
        bugs = json.load(file)

    print('Replacing project names...')
    fixed_data = replace_project_names(bugs)
    with open(DATASET, 'w') as file:
        json.dump(fixed_data, file, indent=2)

    print('Checking project URLs...')
    check_projects()


if __name__ == '__main__':
    main()
