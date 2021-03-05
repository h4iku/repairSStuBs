import csv
import linecache
import shutil
import subprocess
from pathlib import Path

from joblib.parallel import Parallel, delayed
from utils.data_reader import (DATASET, INPUT, REPAIR_OUTPUT, REPAIR_RESULT,
                               ManySStuBs4J, n_jobs)


def create_fixed_file(dir_path, file_name, line_number, fixed_line):

    print(fixed_line)

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


def compare(patch_dir, file_name, bug_line_number, fixed_line):

    fixed_file_comp = create_fixed_file(
        patch_dir, file_name, bug_line_number, fixed_line)

    ast_diff = Path(__file__).parent / 'lib/gumtree-spoon-ast-diff.jar'
    cmd = f'java -jar {ast_diff} {patch_dir/file_name} {fixed_file_comp}'
    try:
        comp_out = subprocess.check_output(
            cmd, shell=True, stderr=subprocess.DEVNULL).decode()

        if 'no AST change' in comp_out:
            return True
        else:
            return False

    except Exception as e:

        # Fallback to comparing simple strings
        with open(patch_dir / file_name) as f:
            lines = f.read().splitlines()
        buggy_line = lines[bug_line_number - 1]
        if buggy_line.replace(' ', '') == fixed_line.strip().replace(' ', ''):
            return True
        else:
            return False


def main():

    bugs = ManySStuBs4J(DATASET).bugs

    bugs = [b for b in bugs][:1]

    REPAIR_RESULT.touch()

    # Retreiving already processed bugs
    with open(REPAIR_RESULT, newline='') as f:
        reader = csv.reader(f)
        processed = {x[0] for x in reader}

    for i, bug in enumerate(bugs):

        print(f'Patch comparing for bug {i}')

        # buggy_file = bug.buggy_file_dir / bug.file_name
        fixed_file = bug.fixed_file_line_dir / bug.file_name

        # If the bug is already processed
        if str(bug.buggy_file_line_dir) in processed:
            continue

        patch_output = REPAIR_OUTPUT / bug.buggy_file_line_dir

        try:
            # FIXME: Use better line retrieval method
            with open(INPUT / fixed_file) as file:
                fixed_line = file.readlines()[bug.bug_line_num - 1]
            # fixed_line = linecache.getline(
            #     str(INPUT / fixed_file), bug.fix_line_num)
        except Exception as e:
            print(e)
            print(INPUT / fixed_file)
            continue

        if not patch_output.exists():
            continue

        # comp_res = Parallel(n_jobs=n_jobs)(
        #     delayed(compare)(patch_dir, bug.file_name,
        #                      bug.bug_line_num, fixed_line)
        #     for patch_dir in sorted(patch_output.iterdir(), key=attrgetter('name'))
        # )

        comp_res = [compare(patch_dir, bug.file_name, bug.bug_line_num, fixed_line)
                    for patch_dir in sorted(patch_output.iterdir(), key=lambda x: int(x.name))]

        patch_result = [str(bug.buggy_file_line_dir), repr(comp_res),
                        bug.project_name, bug.bug_type]

        with open(REPAIR_RESULT, 'a', newline='') as result_csv_file:
            csv_writer = csv.writer(result_csv_file)
            csv_writer.writerow(patch_result)


if __name__ == '__main__':
    main()
