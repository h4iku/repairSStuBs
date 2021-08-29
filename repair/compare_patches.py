import csv
import sys
from pathlib import Path

import jpype
import jpype.imports
from jpype.types import *
from pathos.pools import ProcessPool
from tqdm import tqdm
from utils.config import DATASET, INPUT, REPAIR_OUTPUT, REPAIR_RESULT, n_jobs
from utils.data_reader import ManySStuBs4J


gumtree_spoon = (Path(__file__).parent /
                 'lib/gumtree-spoon-ast-diff-1.35-jar-with-dependencies.jar')
spoon_core = (Path(__file__).parent /
              'lib/spoon-core-9.1.0-jar-with-dependencies.jar')
classpath = [str(gumtree_spoon), str(spoon_core)]
jpype.startJVM(classpath=classpath)

from gumtree.spoon import AstComparator
from spoon import Launcher


def compare(patch_file, line_number, fixed_line, backend):

    with open(patch_file) as f:
        patch_line = f.readlines()[line_number - 1].strip()

    # Since we know that the given line is definitely inside a method
    patch_template = f'class C {{ void m() {{ {patch_line} }} }}'
    fixed_template = f'class C {{ void m() {{ {fixed_line} }} }}'

    try:
        if backend == 'spoon-core':
            patch_class = Launcher.parseClass(patch_template)
            fixed_class = Launcher.parseClass(fixed_template)
            if patch_class.toString() == fixed_class.toString():
                return True
            else:
                return False
        elif backend == 'gumtree-spoon':
            comp_out = AstComparator().compare(patch_template, fixed_template)
            if 'no AST change' in comp_out.toString():
                return True
            else:
                return False

    except Exception as e:

        # print(e, file=sys.stderr)

        # Fallback to comparing strings
        if patch_line.replace(' ', '') == fixed_line.replace(' ', ''):
            return True
        else:
            return False


def main():

    # Backend can be either `spoon-core` or `gumtree-spoon`
    backend = 'spoon-core'
    pool = ProcessPool(nodes=n_jobs)

    bugs = ManySStuBs4J(DATASET).bugs
    REPAIR_RESULT.touch()

    # Retreiving already processed bugs
    with open(REPAIR_RESULT, newline='') as f:
        reader = csv.reader(f)
        processed = {(x[0], x[-1]) for x in reader}

    for bug in tqdm(bugs, total=len(bugs)):

        fixed_file = bug.fixed_file_line_dir / bug.file_name

        # If the bug is already processed
        # This is only for resume after interruption. It won't prevent duplicates.
        if (str(bug.buggy_file_line_dir), bug.bug_type) in processed:
            continue

        patch_output = REPAIR_OUTPUT / bug.buggy_file_line_dir

        if not patch_output.exists():
            continue

        try:
            with open(INPUT / fixed_file) as file:
                fixed_line = file.readlines()[bug.fix_line_num - 1].strip()
        except Exception as e:
            print(e, file=sys.stderr)
            print(INPUT / fixed_file, file=sys.stderr)
            continue

        patch_files = [path_dir / bug.file_name
                       for path_dir in sorted(patch_output.iterdir(), key=lambda x: int(x.name))]
        pfnum = len(patch_files)
        comp_res = pool.map(compare, patch_files, [bug.bug_line_num] * pfnum,
                            [fixed_line] * pfnum, [backend] * pfnum)

        patch_result = [str(bug.buggy_file_line_dir), repr(comp_res),
                        bug.project_name, bug.bug_type]

        with open(REPAIR_RESULT, 'a', newline='') as result_csv_file:
            csv_writer = csv.writer(result_csv_file)
            csv_writer.writerow(patch_result)


if __name__ == '__main__':
    main()
