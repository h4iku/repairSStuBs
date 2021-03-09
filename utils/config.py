from pathlib import Path

n_jobs = 4

ROOT = Path(__file__).parent

DATASET_ROOT = ROOT / '../data'
SRC_FILES = DATASET_ROOT / 'src_files'
INPUT = DATASET_ROOT / 'input'

REPAIR_ROOT = ROOT / '../repair'
REPAIR_OUTPUT = REPAIR_ROOT / 'result/repair_output'
REPAIR_RESULT = REPAIR_ROOT / 'result/repair_result.csv'

DETECT_ROOT = ROOT / '../detect'

sstubs = DATASET_ROOT / 'sstubs.json'
bugs = DATASET_ROOT / 'bugs.json'
sstubs_large = DATASET_ROOT / 'sstubsLarge.json'
bugs_large = DATASET_ROOT / 'bugsLarge.json'

DATASET = sstubs
