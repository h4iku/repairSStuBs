import csv
import shutil
import subprocess
from pathlib import Path

from joblib.parallel import Parallel, delayed
from utils.data_reader import (DATASET, INPUT, REPAIR_OUTPUT, REPAIR_RESULT,
                               ManySStuBs4J, n_jobs)


def create_fixed_file(dir_path, file_name, line_number, fixed_line):

    # Copy generated file
    fixed_file_comp = shutil.copyfile(
        dir_path/file_name, dir_path/f'fixed_{file_name}')

    # Replacing the patched line with the actual fixed one
    with open(fixed_file_comp, 'r+') as f:
        lines = f.read().splitlines()
        lines[line_number - 1] = fixed_line.rstrip()
        f.seek(0)
        f.truncate()
        f.write('\n'.join(lines))

    return fixed_file_comp


def compare(patched_file, fixed_comp_file, line_number, fixed_line):

    ast_diff = (Path(__file__).parent /
                'lib/gumtree-spoon-ast-diff-1.30-jar-with-dependencies.jar')
    cmd = ['java', '-jar', ast_diff, patched_file, fixed_comp_file]
    try:
        comp_out = subprocess.check_output(cmd).decode()

        if 'no AST change' in comp_out:
            return True
        else:
            return False

    except Exception as e:

        # Fallback to comparing strings
        with open(patched_file) as f:
            lines = f.read().splitlines()
        buggy_line = lines[line_number - 1]

        if buggy_line.strip().replace(' ', '') == fixed_line.strip().replace(' ', ''):
            return True
        else:
            return False


def main():

    bugs = ManySStuBs4J(DATASET).bugs

    REPAIR_RESULT.touch()

    # Retreiving already processed bugs
    with open(REPAIR_RESULT, newline='') as f:
        reader = csv.reader(f)
        processed = {x[0] for x in reader}

    for i, bug in enumerate(bugs):

        print(f'Patch comparing for bug {i}')

        fixed_file = bug.fixed_file_line_dir / bug.file_name

        # If the bug is already processed
        if str(bug.buggy_file_line_dir) in processed:
            continue

        patch_output = REPAIR_OUTPUT / bug.buggy_file_line_dir

        if not patch_output.exists():
            continue

        try:
            with open(INPUT / fixed_file) as file:
                fixed_line = file.readlines()[bug.bug_line_num - 1]
        except Exception as e:
            print(e)
            print(INPUT / fixed_file)
            continue

        fixed_comp_file = create_fixed_file(
            INPUT / bug.buggy_file_line_dir,
            bug.file_name, bug.bug_line_num, fixed_line)

        comp_res = Parallel(n_jobs=n_jobs)(
            delayed(compare)(patch_dir / bug.file_name, fixed_comp_file,
                             bug.bug_line_num, fixed_line)
            for patch_dir in sorted(patch_output.iterdir(), key=lambda x: int(x.name))
        )

        Path.unlink(fixed_comp_file)

        patch_result = [str(bug.buggy_file_line_dir), repr(comp_res),
                        bug.project_name, bug.bug_type]

        with open(REPAIR_RESULT, 'a', newline='') as result_csv_file:
            csv_writer = csv.writer(result_csv_file)
            csv_writer.writerow(patch_result)


if __name__ == '__main__':
    main()
