# Detecting simple stupid bugs (SStuBs) using code changes and repairing them with a seq2seq model

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

This package contains a simple example-based bug detection tool that uses a feed-forward neural network classifier.

**`prepare.py`:**
Uses `fixPatch` field of each SStuB and extracts the patched lines of the code changes (i.e., the ones starting with ‘+’) as well as the patch context lines. It then tokenizes these to learn word embeddings using [Doc2Vec](https://radimrehurek.com/gensim_3.8.3/models/doc2vec.html). The whole data is used to train 100-dimensional vectors with a window size of 10 around each token. These parameters can change in the `build_embedding()` function.

**`classify.py`:**
Uses the output lines of `utils/line_normalize.py` to build a bug detection model for each bug pattern. For each line, it infers a vector from the embedding model as the input to the classifier. Bug pattern is specified using the ‍`bug_type` variable, and its values are the same as the ones in the dataset, which are described in the [mineSStuBs repository](https://github.com/mast-group/mineSStuBs). The classifier is a feed-forward neural network with two hidden layers.


### `repair`

This package generates patches and tries to repair the SStuBs.

**`get_patches.py`:**
Uses [SequenceR](https://github.com/KTH/chai) to generate patches for each SStuB. You should install SequenceR separately for this to work. The directory where SequenceR installed is specified in the `sequencer_home` variable. By default, it points to the home directory of the operating system. The beam size is also set to 50.

**`compare_patches.py`:**
After getting patches, it's time to find if the bug is repaired or not. [Gumtree Spoon AST Diff](https://github.com/SpoonLabs/gumtree-spoon-ast-diff/) is used to compare generated patches with the actual fix. You need to have Java 11 installed for Gumtree Spoon AST Diff to work. We copy the patched file and replace the patched line with the fixed line to have two identical source files with only one line of difference. Then AST Diff is used to see if the patched line is the same as the fix line. We don't use the source file from the fix commit for this comparison since a commit may contain other changes to a file.

**`evaluate.py`:**
Results from the patch comparison of the previous module are written to a file. This module parses this result file and prints out evaluations like total generated patches, the number of repaired bugs and grouping repaired bugs by bug patterns.


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
