'''Some parts of this module are adapted from:
https://github.com/SerVal-DTF/DL4PatchCorrectness/tree/master/preprocess
'''

import json
import re

import nltk
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from utils.config import DATASET, EMBED_MODEL, PATCH_TOKENS, n_jobs
from utils.data_reader import ManySStuBs4J


def get_diff_files_frag(patch, type):
    '''Separates buggy lines from patched lines using
    + and - in front of each line based on the given type.
    Ignores lines with only comments. Then tokenizes given
    `patch` using a regex, and then concatenates them together.
    '''

    lines = ''
    p = r"([^\w_])"
    flag = True
    for line in patch:
        line = line.strip()
        if '*/' in line:
            flag = True
            continue
        if flag == False:
            continue
        if line != '':
            if line.startswith('@@') or line.startswith('diff') or line.startswith('index') or line.startswith('Binary'):
                continue
            elif '/*' in line:
                flag = False
                continue
            elif type == 'buggy':
                if line.startswith('---') or line.startswith('PATCH_DIFF_ORIG=---'):
                    line = re.split(
                        pattern=p, string=line.split(' ')[1].strip())
                    lines += ' '.join(line) + ' '
                elif line.startswith('-'):
                    if line[1:].strip().startswith('//'):
                        continue
                    line = re.split(pattern=p, string=line[1:].strip())
                    line = [x.strip() for x in line]
                    while '' in line:
                        line.remove('')
                    line = ' '.join(line)
                    lines += line.strip() + ' '
                elif line.startswith('+'):
                    pass
                else:
                    line = re.split(pattern=p, string=line.strip())
                    line = [x.strip() for x in line]
                    while '' in line:
                        line.remove('')
                    line = ' '.join(line)
                    lines += line.strip() + ' '
            elif type == 'patched':
                if line.startswith('PATCH_DIFF_ORIG=---'):
                    continue
                elif line.startswith('+++'):
                    line = re.split(
                        pattern=p, string=line.split(' ')[1].strip())
                    lines += ' '.join(line) + ' '
                elif line.startswith('+'):
                    if line[1:].strip().startswith('//'):
                        continue
                    line = re.split(pattern=p, string=line[1:].strip())
                    line = [x.strip() for x in line]
                    while '' in line:
                        line.remove('')
                    line = ' '.join(line)
                    lines += line.strip() + ' '
                elif line.startswith('-'):
                    pass
                else:
                    line = re.split(pattern=p, string=line.strip())
                    line = [x.strip() for x in line]
                    while '' in line:
                        line.remove('')
                    line = ' '.join(line)
                    lines += line.strip() + ' '
    return lines


def create_train_data_frag(path_patch_train):
    """Returns buggy and patched tokens of diffs as a dict.
    """

    data = []  # json list
    for bug in path_patch_train:

        # FIXME: Find a better id, since commit hash is not unique for each bug.
        bug_id = bug.fix_commit_sha1

        buggy = get_diff_files_frag(
            bug.fix_patch.splitlines(), type='buggy')
        patched = get_diff_files_frag(
            bug.fix_patch.splitlines(), type='patched')

        if buggy == '' or patched == '':
            print('null patch')
            continue
        sample = {'bug_id': bug_id, 'buggy': buggy, 'patched': patched}
        data.append(sample)

    return data


def build_embedding(df):

    vector_size = 100

    data = []
    for bug in df:
        bug['buggy'] = nltk.wordpunct_tokenize(bug['buggy'])
        bug['patched'] = nltk.wordpunct_tokenize(bug['patched'])
        data.append(list(bug['buggy']))
        data.append(list(bug['patched']))

    documents = [TaggedDocument(doc, [i]) for i, doc in enumerate(data)]
    model = Doc2Vec(documents, vector_size=vector_size,
                    window=10, min_count=1, workers=n_jobs)
    model.save(str(EMBED_MODEL))


def main():

    sstubs = ManySStuBs4J(DATASET).bugs
    d = create_train_data_frag(sstubs)

    with open(PATCH_TOKENS, 'w+') as file:
        json.dump(d, file, indent=4)

    build_embedding(d)


if __name__ == '__main__':
    main()
