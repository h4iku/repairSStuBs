# Detecting simple stupid bugs (SStuBs) using code changes and repairing them with a seq2seq model

Some code to work with the [ManySStuBs4J dataset](https://doi.org/10.5281/zenodo.3653444), which is a collection of simple fixes to single line Java bugs.

## Repository Description

### `utils`:

This package contains some utility modules to fix and prepare the data.

**`data_reader.py`:**
Loads the `json` dataset and puts SStuB properties into a `Bug` class. It defines some useful methods like generating GitHub URLs to be used in other modules or the directory paths to access source files.

**`config.py`:**
Contains configuration variables for dataset paths and other assets:

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

These downloaded source files are also available here:

| sstubs | bugs | sstubsLarge | bugsLarge |
|--------|------|-------------|-----------|
| [sstubs_src_files.zip](https://www.mediafire.com/file/ry8zs6u14bdl4dp/sstubs_src_files.zip/file) | [bugs_src_files.zip](https://www.mediafire.com/file/8933v6lyig3zhb7/bugs_src_files.zip/file) | sstubsLarge_src_files.zip | bugsLarge_src_files.zip |

**`line_normalize.py`:**
Line numbers in the dataset are sometimes off, and for example, point to comment multiple lines before the actual intended line. Moreover, sometimes the programmer has broken a single Java statement into multiple lines, and the line number is only pointing to a part of this statement. Therefore, It is needed to normalize these cases by moving up and down the lines and checking for Java language specific separators (e.g., { and ;) to collect the complete Java statement. This is especially needed for the tool used in the `repair` part to generate patches since it needs the given buggy line to be complete Java statements and not just part of a statement.


### `detect`:

This package contains a simple example-based bug detection tool that uses a feed-forward neural network classifier.

**`prepare.py`:**


### `repair`:

This package uses SequenceR to repair bugs.
