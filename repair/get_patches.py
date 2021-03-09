import subprocess
from pathlib import Path

from utils.config import DATASET, INPUT, REPAIR_OUTPUT
from utils.data_reader import ManySStuBs4J


def main():

    bugs = ManySStuBs4J(DATASET).bugs

    sequencer_home = Path.home() / 'chai'
    beam_size = 50
    predictor = sequencer_home / 'src/sequencer-predict.sh'
    model = sequencer_home / 'model/model.pt'

    for bug in bugs:

        input = INPUT / bug.buggy_file_line_dir / bug.file_name
        patch_output = REPAIR_OUTPUT / bug.buggy_file_line_dir

        # If input file doesn't exist or patches are already generated for this file and line number
        if not input.exists() or patch_output.exists():
            continue

        cmd = f'{predictor} \
            --model={model} \
            --buggy_file={input.resolve()} \
            --buggy_line={bug.bug_line_num} \
            --beam_size={beam_size} \
            --output={patch_output.resolve()}'

        subprocess.call(cmd, shell=True)


if __name__ == '__main__':
    main()
