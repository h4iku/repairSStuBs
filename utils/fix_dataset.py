import json
from pathlib import Path


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
        'b3log.symphony': '88250.symphony'
    }

    # Without user part with only repository name
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
    pass


def main():

    # Make path relative to current module
    data_path = Path(__file__).parent / '../data'

    with open(data_path / 'sstubs.json') as file:
        bugs = json.load(file)

    fixed_data = replace_project_names(bugs)
    with open(data_path / 'sstubs.json', 'w') as file:
        json.dump(fixed_data, file, indent=2)


if __name__ == '__main__':
    main()
