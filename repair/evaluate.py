import csv
import difflib
import shutil
from collections import defaultdict
from statistics import mean

from pytablewriter import MarkdownTableWriter
from tqdm import tqdm
from utils.config import CORRECT_PATCHES, INPUT, REPAIR_OUTPUT, REPAIR_RESULT


class Result:

    def __init__(self, buggy_file_line_dir, comparison_result,
                 fixed_file_line_dir, file_name, project_name, bug_type):
        self.buggy_file_line_dir = buggy_file_line_dir
        self.comparison_result = eval(comparison_result)
        self.fixed_file_line_dir = fixed_file_line_dir
        self.file_name = file_name
        self.project_name = project_name
        self.bug_type = bug_type

        self.buggy_file = INPUT / self.buggy_file_line_dir / self.file_name
        self.fixed_file = INPUT / self.fixed_file_line_dir / self.file_name

        if self.fix_patch_number():
            self.genfixed_file = (REPAIR_OUTPUT / self.buggy_file_line_dir /
                                  str(self.fix_patch_number()) / self.file_name)
        else:
            self.genfixed_file = None

    def __eq__(self, other):
        return (self.buggy_file_line_dir == other.buggy_file_line_dir
                and self.bug_type == other.bug_type)

    def fix_patch_number(self):
        if True in self.comparison_result:
            return self.comparison_result.index(True) + 1
        else:
            return None

    def copy_files(self):
        """Copies result files to a designated directory"""

        # Create the destination directory
        copy_path = (CORRECT_PATCHES / self.buggy_file_line_dir)
        copy_path.mkdir(parents=True, exist_ok=True)

        # Copy the buggy file
        shutil.copyfile(self.buggy_file, copy_path / 'BuggyFile.java')

        # Copy the actual fixed file
        shutil.copyfile(self.fixed_file, copy_path / 'FixedFile.java')

        # Copy the correctly generated fixed file
        shutil.copyfile(self.genfixed_file, copy_path /
                        'GeneratedFixFile.java')

    def generate_diffs(self):

        save_path = (CORRECT_PATCHES / self.buggy_file_line_dir)
        save_path.mkdir(parents=True, exist_ok=True)

        # Diff between buggy file and actual fixed file
        with open(self.buggy_file) as buggy_file:
            with open(self.fixed_file) as fixed_file:
                bugfix_diff = difflib.unified_diff(
                    buggy_file.readlines(),
                    fixed_file.readlines(),
                    fromfile='BuggyFile.java', tofile='FixedFile.java'
                )
        with open(save_path / 'bugfix.diff', 'w') as bugfix_file:
            bugfix_file.writelines(bugfix_diff)

        # Diff between buggy file and the generated fixed file
        with open(self.buggy_file) as buggy_file:
            with open(self.genfixed_file) as genfixed_file:
                genfix_diff = difflib.unified_diff(
                    buggy_file.readlines(),
                    genfixed_file.readlines(),
                    fromfile='BuggyFile.java', tofile='GeneratedFixFile.java'
                )
        with open(save_path / 'genfix.diff', 'w') as genfix_file:
            genfix_file.writelines(genfix_diff)


def main():

    with open(REPAIR_RESULT, newline='') as file:
        reader = csv.reader(file)
        all_results = [Result(*line) for line in reader]

    # Removing duplicates
    results = []
    for result in all_results:
        if result not in results:
            results.append(result)

    # Copying results and generating diffs
    for res in tqdm(results):
        if res.fix_patch_number():
            res.copy_files()
            res.generate_diffs()

    # Evaluating
    total_gen_patches = [res.comparison_result for res in results]
    num_total_gen_patches = [len(x) for x in total_gen_patches]
    print(f'Total generated patches: {sum(num_total_gen_patches)}')
    print(f'min: {min(num_total_gen_patches)}, '
          f'max: {max(num_total_gen_patches)}, '
          f'avg: {mean(num_total_gen_patches)}')

    num_fixes = [1 for x in total_gen_patches if any(x)]
    print(f'Total bugs: {len(results)}', f'Fixed: {sum(num_fixes)}')

    patterns = defaultdict(lambda: [0, 0, []])
    for res in results:
        gen_patches = res.comparison_result
        patterns[res.bug_type][-1].append(len(gen_patches))
        if any(gen_patches):
            patterns[res.bug_type][0] += 1
            patterns[res.bug_type][1] += 1
        else:
            patterns[res.bug_type][0] += 1

    print('Number of min, max, avg generated patches:')
    print([(ptn, min(vals[-1]), max(vals[-1]), mean(vals[-1]))
           for ptn, vals in patterns.items()])

    # Sort by the number of bugs
    patterns_list = sorted(patterns.items(),
                           key=lambda x: x[1][0], reverse=True)
    value_matrix = [
        [ptn] + vals[:-1] + [f'{(vals[1] / vals[0]) * 100:.2f}%']
        for ptn, vals in patterns_list
    ]
    value_matrix.append(
        ['Total', sstubs := len(results),
         corrects := sum(num_fixes),
         f'{(corrects / sstubs) * 100:.2f}%']
    )

    # Configuring the Markdown table
    writer = MarkdownTableWriter(
        table_name="repair_results",
        headers=["Pattern Name", "SStuBs", "Correct Patches", "Ratio"],
        value_matrix=value_matrix,
    )
    writer.write_table()


if __name__ == '__main__':
    main()
