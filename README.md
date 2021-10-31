# Detecting simple stupid bugs (SStuBs) using pre-trained transformer and repairing them with seq2seq model

Some code to work with the [ManySStuBs4J dataset](https://doi.org/10.5281/zenodo.3653444), which is a collection of simple fixes to single line Java bugs.

## Repository Description

### `utils`

This package contains some utility modules to fix and prepare the data.

**`data_reader.py`:**
Loads the `json` dataset and puts SStuB properties into a `Bug` class. It defines some useful methods like generating GitHub URLs to be used in other modules or the directory paths to access source files.

**`config.py`:**
Contains configuration variables for dataset paths and other assets. By default, datasets reside in the data directory in the root of the repository:

```python
DATASET_ROOT = '../data'
SRC_FILES = DATASET_ROOT / 'src_files'

sstubs = DATASET_ROOT / 'sstubs.json'
bugs = DATASET_ROOT / 'bugs.json'
sstubs_large = DATASET_ROOT / 'sstubsLarge.json'
bugs_large = DATASET_ROOT / 'bugsLarge.json'
```

**`fix_dataset.py`:**
Some projects in the dataset are removed from GitHub or moved to another repository (e.g., `b3log.solo` has moved to `88250.solo`). This module replaces them with an appropriate fork or a new repository that contains the same history to have access to its commits and files. Furthermore, especially in the large version, some project names only contain the repository name (e.g., `struts` that should be `apache.struts`). Therefore, we manually found and completed their repository owner part. After replacing correct project names, GitHub URL for each project is built and checked if the project exists on GitHub.

**`retrieve_files.py`:**
Downloads fixed and buggy source files based on the commit hashes given for each bug. The download process is concurrent, and the maximum number of jobs can be specified using the `n_jobs` variable in `config.py`. The directory structure of retrieved source files is like this:

```
username.repository/commit_hash/dotted_file_path/file.java
```

For example

```
https://github.com/apache/camel/commit/d55fc4de68d1c8d9a5aff883e2c5f84ad02aa0b8/components/camel-restlet/src/test/java/org/apache/camel/component/restlet/RestletConfigurationTest.java
```

is saved in:

```
apache.camel/d55fc4de68d1c8d9a5aff883e2c5f84ad02aa0b8/components.camel-restlet.src.test.java.org.apache.camel.component.restlet/RestletConfigurationTest.java
```

The downloaded source files are also available here:

| all | sstubs | bugs | sstubsLarge | bugsLarge |
|-----|--------|------|-------------|-----------|
[`all_src_files.zip`](https://www.mediafire.com/file/q68ejrted7hfxtq/all_src_files.zip/file) | [`sstubs_src_files.zip`](https://www.mediafire.com/file/ry8zs6u14bdl4dp/sstubs_src_files.zip/file) | [`bugs_src_files.zip`](https://www.mediafire.com/file/8933v6lyig3zhb7/bugs_src_files.zip/file) | [`sstubsLarge_src_files.zip`](https://www.mediafire.com/file/6y3fziwvof3nucp/sstubsLarge_src_files.zip/file) | [`bugsLarge_src_files.zip`](https://www.mediafire.com/file/66ekj086uit5dk4/bugsLarge_src_files.zip/file) |

These files have the replaced project names for deleted or moved projects from `fix_dataset.py`.

**`line_normalize.py`:**
Line numbers in the dataset are sometimes off, and for example, point to comment multiple lines before the actual intended line. Moreover, sometimes the programmer has broken a single Java statement into multiple lines, and the line number is only pointing to a part of this statement. Therefore, It is needed to normalize these cases by moving up and down the lines and checking for Java language specific separators like `{` and `;` to collect the complete Java statement. This is especially needed for the tool used in the `repair` part to generate patches since it needs the given buggy line to be complete Java statements and not just part of a statement.

This module does this normalization using a heuristic and saves new source files in a directory like

```
username.repository/commit_hash/dotted_file_path/filename.java/line_number
```

where `line_number` shows which line is normalized. These line numbers are the same as the ones in the dataset.


### `detect`

This package contains a simple example-based bug detection tool that uses a pre-trained transformer for the bug classification task.

**`build_model.py`:**
Fine-tunes a [pre-trained CodeBERTa model](https://huggingface.co/huggingface/CodeBERTa-small-v1) to build a bug detection model for all the bug types described in the [mineSStuBs repository](https://github.com/mast-group/mineSStuBs). Fine-tuning is based on `source_before_fix` and `source_after_fix` fields of the dataset for buggy and fixed examples, respectively. During fine-tuning, the checkpoints save in the `utils.config.DETECT_RESULT` directory for each epoch and can be used to further train or predict bugs.


### `repair`

This package generates patches and tries to repair the SStuBs.

**`get_patches.py`:**
Uses [SequenceR](https://github.com/KTH/chai) to generate patches for each SStuB. You should install SequenceR separately for this to work. The directory where SequenceR installed is specified in the `sequencer_home` variable. By default, it points to the home directory of the operating system. The beam size is also set to 50.

**`compare_patches.py`:**
After getting patches, it's time to find if the bug is repaired or not. The comparison is done between the generated patch line and the fixed line of the fix commit. Two methods can be used to compare these two lines:

- `spoon-core`: That relies on [Spoon](https://spoon.gforge.inria.fr/)'s default [pretty-printing](https://spoon.gforge.inria.fr/custom-pretty-printing.html) to uniformize separators and whitespaces.
- `gumtree-spoon`: That uses the snippet compare functionality of [Gumtree Spoon AST Diff](https://github.com/SpoonLabs/gumtree-spoon-ast-diff/).

The default compare backend is `spoon-core`, but it can change using the `backend` variable in the `main` function of this module. You need Java 11 installed for these to work.

**`evaluate.py`:**
Results from the patch comparison of the previous module are written to `repair_result.csv`. This module parses this file and prints out evaluations like total generated patches, the number of repaired bugs, and the number repaired bugs grouped by bug patterns.

The generated patches for the `sstubs.json` version of the dataset and the correct ones detected using the `spoon-core` backend can be downloaded from this table:

| Generated Patches | Correct Patches |
|-------------------|-----------------|
| [`repair_output.zip`](https://www.mediafire.com/file/jd9byxt3qcxy7bu/repair_output.zip/file) | [`correct_patches.zip`](https://www.mediafire.com/file/m6qfoukssknuhvi/correct_patches.zip/file) |

In this output, a total of 250861 patches are generated for 6430 bugs with an average of 39.01 patches for each bug. Out of these, 1266 bugs got a correct patch. The following table shows the detailed result for each bug pattern.

|         Pattern Name         |SStuBs|Correct Patches| Ratio |
|------------------------------|-----:|--------------:|------:|
|CHANGE_IDENTIFIER             |  2332|            350| 15.01%|
|DIFFERENT_METHOD_SAME_ARGS    |  1365|            136| 9.96% |
|CHANGE_NUMERAL                |   744|            202| 27.15%|
|OVERLOAD_METHOD_MORE_ARGS     |   649|             62| 9.55% |
|CHANGE_OPERATOR               |   237|            135| 56.96%|
|CHANGE_CALLER_IN_FUNCTION_CALL|   169|             34| 20.12%|
|CHANGE_UNARY_OPERATOR         |   154|            100| 64.94%|
|OVERLOAD_METHOD_DELETED_ARGS  |   154|             92| 59.74%|
|MORE_SPECIFIC_IF              |   151|             20| 13.25%|
|LESS_SPECIFIC_IF              |   132|              7| 5.30% |
|SWAP_ARGUMENTS                |   117|             10| 8.55% |
|SWAP_BOOLEAN_LITERAL          |   111|             86| 77.48%|
|CHANGE_OPERAND                |    92|             20| 21.74%|
|CHANGE_MODIFIER               |    23|             12| 52.17%|
|Total                         |  6430|           1266| 19.69%|


## How To Use

1. Install Python 3.8+ and clone this repository:

    ```bash
    git clone https://github.com/h4iku/repairSStuBs.git
    cd repairSStuBs
    ```

2. Create a virtual environment and activate it:

    ```bash
    python -m venv env
    # On Windows:
    env\Scripts\activate
    # Or on Linux:
    source env/bin/activate
    ```

    Then install the dependencies:

    ```
    python -m pip install -U pip setuptools
    pip install -r requirements.txt
    ```

3. To run each module, step outside its package (so you are at the root of the repository) and type:

    ```
    python -m package.module
    ```

    For example, to run the `retrieve_files.py` module:

    ```
    python -m utils.retrieve_files
    ```

    To run tests:

    ```
    python -m unittest discover -s tests
    ```

    Modules in each package have an order of execution, and they work on top of each other's output. The order is intuitive according to their names, and it's the same order as they are described above.

    Also, don't forget to install Java and SequenceR for the repair part.
