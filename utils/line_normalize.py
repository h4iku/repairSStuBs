import re
from pathlib import Path

from .config import DATASET, INPUT, SRC_FILES
from .data_reader import ManySStuBs4J


def check_line(lines, line_number):
    """This function tries to extract the complete bug line
    when it is expanded on multiple lines or the line number
    in the dataset is pointing to somewhere else like comments
    before reaching the actual line, etc.
    """

    # Regex patterns for single and multiline comments
    single_comment = r'(?<!:)\/\/.*(?<!\>)'
    multi_comment = r'\/\*(.|\s)*?\*\/'

    target_line = lines[line_number].strip()
    # First multiline, then single line to avoid `/* // */`
    stripped_line = re.sub(multi_comment, '', target_line).strip()
    stripped_line = re.sub(single_comment, '', target_line).strip()

    prev_line = re.sub(multi_comment, '', lines[line_number - 1]).strip()
    prev_line = re.sub(single_comment, '', lines[line_number - 1]).strip()

    # The given line is a multiline comment
    if stripped_line.startswith('/*'):

        while '*/' not in lines[line_number].strip():
            del lines[line_number]
        del lines[line_number]
        return check_line(lines, line_number)

    # If the line is empty
    elif not stripped_line:

        del lines[line_number]
        return check_line(lines, line_number)

    else:
        new_lines = lines[:]
        new_line = stripped_line
        i = line_number - 1

        while not prev_line.endswith((';', '{', '}', ':')):
            new_line = prev_line + ' ' + new_line
            new_lines[i] = ''
            i -= 1
            prev_line = re.sub(multi_comment, '', new_lines[i]).strip()
            prev_line = re.sub(single_comment, '', new_lines[i]).strip()

        # We also need to go down if it's a middle line of a statement
        while not stripped_line.endswith((';', '{', ':')):

            # The block is closed on the statement line
            if stripped_line.endswith('}'):
                del new_lines[line_number]
                new_lines.insert(line_number, '}')
                new_line = re.sub(multi_comment, '', new_line[:-1]).strip()
                new_lines.insert(line_number, new_line)
                return new_lines

            del new_lines[line_number]
            stripped_line = re.sub(
                multi_comment, '', new_lines[line_number]).strip()
            stripped_line = re.sub(
                single_comment, '', new_lines[line_number]).strip()
            new_line += f' {stripped_line}'

        del new_lines[line_number]

        # Because going up we might have captured a complete multiline comment
        # until reaching a separator.
        new_line = re.sub(multi_comment, '', new_line).strip()
        new_lines.insert(line_number, new_line)
        return new_lines


def normalize(src_dir, save_dir, file_name, line_number):

    output = (INPUT / save_dir)

    if not output.exists():
        with open(SRC_FILES / src_dir / file_name) as f:
            lines = f.read().splitlines()

        try:
            normalized_lines = check_line(lines, line_number - 1)
        except:
            # Because some line numbers point to a nonexisting line in the file.
            # Example:
            # https://github.com/JetBrains/intellij-community/commit/1876ac4a290bfeb7a4321c3232169dabd97367cf/source/com/intellij/lexer/__XmlLexer.java
            # with fixline of 824
            print(Path(src_dir / file_name), line_number)
            return

        output.mkdir(parents=True, exist_ok=True)
        with open(output / file_name, 'w') as f:
            f.write('\n'.join(normalized_lines))


def main():

    bugs = ManySStuBs4J(DATASET).bugs

    for bug in bugs:

        parameters = [
            (bug.buggy_file_dir, bug.buggy_file_line_dir,
             bug.file_name, bug.bug_line_num),
            (bug.fixed_file_dir, bug.fixed_file_line_dir,
             bug.file_name, bug.fix_line_num)
        ]

        for param in parameters:
            normalize(*param)


if __name__ == '__main__':
    main()
