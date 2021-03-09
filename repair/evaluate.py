import csv
from collections import defaultdict
from statistics import mean

from utils.config import REPAIR_RESULT


def main():

    # TODO: It would be nice to read the results back into a proper object

    with open(REPAIR_RESULT, newline='') as file:
        reader = csv.reader(file)
        total = [line for line in reader]

    total_gen_patches = [eval(line[1]) for line in total]
    num_total_gen_patches = [len(x) for x in total_gen_patches]
    print(f'Total generated pateches: {sum(num_total_gen_patches)}')
    print(f'min: {min(num_total_gen_patches)}, '
          f'max: {max(num_total_gen_patches)}, '
          f'avg: {mean(num_total_gen_patches)}')

    num_fixes = [1 for x in total_gen_patches if any(x)]
    print(f'Total bugs: {len(total)}', f'Fixed: {sum(num_fixes)}')

    patterns = defaultdict(lambda: [0, 0, []])
    for line in total:
        gen_patches = eval(line[1])
        patterns[line[-1]][-1].append(len(gen_patches))
        if any(gen_patches):
            patterns[line[-1]][0] += 1
            patterns[line[-1]][1] += 1
        else:
            patterns[line[-1]][0] += 1

    patterns_list = {x: y[:-1] for x, y in patterns.items()}
    print(sorted(patterns_list.items(),
                 key=lambda x: x[1][1], reverse=True))
    print([(x, min(y[-1]), max(y[-1]), mean(y[-1]))
           for x, y in patterns.items()])


if __name__ == '__main__':
    main()
