# Detecting simple stupid bugs (SStuBs) using code changes and repairing them with a seq2seq model

Some code to work with the [ManySStuBs4J dataset](https://doi.org/10.5281/zenodo.3653444) which is a collection of simple fixes to one liner Java bugs.

## Repository Description

### `utils`:

This package contains some utility modules to fix and prepare the data.

- `data_reader.py`: Loads the `json` dataset and puts SStuB properties into a `Bug` class. It defines some useful functions like generating GitHub URLs to be used in other modules. There are also configuration variables regarding the path of datasets and other assets:
```python
DATASET_ROOT = '../data'
SRC_FILES = DATASET_ROOT / 'src_files'

sstubs = DATASET_ROOT / 'sstubs.json'
bugs = DATASET_ROOT / 'bugs.json'
sstubs_large = DATASET_ROOT / 'sstubsLarge.json'
bugs_large = DATASET_ROOT / 'bugsLarge.json'
```

- `fix_dataset.py`: Some projects in the dataset were removed from GitHub or moved to another repository, so this module replaces them with an appropriate fork or new repository that contains the same history to have access its commits and files. Some project names also only contained the repository name (in the large version of the dataset), so I manually found and completed their repository owner part. After replacing correct project names, GitHub URL for each project is built and checked if the project actually exists on GitHub.

### `detect`:

This package contains a simple example-based bug detection tool that uses a feed-forward neural network classifier.

### `repair`:

| Pattern Name                   	| SStuBs 	| Correct Fixes 	| Ratio  	| Avg. Patches 	 |
|--------------------------------	|-------:	|--------------:	|--------:	|--------------:|
| `CHANGE_IDENTIFIER`              	|   2429 	|           399 	| 16.43% 	| 38.96        	 |
| `CHANGE_NUMERAL`                 	|    754 	|           201 	| 26.66% 	| 37.84        	 |
| `CHANGE_OPERATOR`                	|    250 	|           143 	| 57.2%  	| 43.39        	 |
| `DIFFERENT_METHOD_SAME_ARGS`     	|   1422 	|           133 	| 9.35%  	| 38.70        	 |
| `CHANGE_UNARY_OPERATOR`          	|    161 	|            96 	| 59.63% 	| 39.47        	 |
| `OVERLOAD_METHOD_DELETED_ARGS`   	|    162 	|            88 	| 54.32% 	| 40.31        	 |
| `SWAP_BOOLEAN_LITERAL`           	|    112 	|            79 	| 70.54% 	| 41.86        	 |
| `OVERLOAD_METHOD_MORE_ARGS`      	|    662 	|            70 	| 10.57% 	| 38.29        	 |
| `CHANGE_CALLER_IN_FUNCTION_CALL` 	|    177 	|            34 	| 19.21% 	| 41.31        	 |
| `CHANGE_OPERAND`                 	|     93 	|            25 	| 26.88% 	| 41.01        	 |
| `MORE_SPECIFIC_IF`               	|    154 	|            21 	| 13.64% 	| 39.08        	 |
| `SWAP_ARGUMENTS`                 	|    120 	|            14 	| 11.67% 	| 36.40        	 |
| `CHANGE_MODIFIER`                	|     23 	|            12 	| 52.17% 	| 37.39        	 |
| `LESS_SPECIFIC_IF`               	|    187 	|             9 	| 4.81%  	| 39.53        	 |
| **Total**                        |   6706 	|          1324 	| 19.74% 	| 39.03        	 |
