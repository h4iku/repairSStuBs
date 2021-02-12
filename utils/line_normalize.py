import json
import re
from pathlib import Path

import bugs_reader


def get_info(bug):
    user_repo = bug['projectName'].split('.')
    user, repo = user_repo[0], '.'.join(user_repo[1:])
    fix_commit = bug['fixCommitSHA1']
    fix_commit_parent = bug['fixCommitParentSHA1']
    file_path = bug['bugFilePath']
    bug_line_number = bug['bugLineNum']
    fix_line_number = bug['fixLineNum']

    return user, repo, fix_commit, fix_commit_parent, file_path, bug_line_number, fix_line_number

# FIXME: Write a util function to generate paths


def check_line(lines, line_number):
    """This function tries to extract the complete bug line
    when it is expanded on multiple lines or the line number
    in the dataset is pointing to somewhere else like comments
    before reaching the actual line, etc.

    However, the function became jank so fast trying to cover all
    the cases. I know, I should've used a parser or something.
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

    # It's a method call on a previous line object and you should go up or
    # function parameters are broken into multiple lines.
    # FIXME: I should refine these rules to be more general, instead of adding cases on top of eachother.

    # Single statement on one line
    # elif stripped_line.endswith((';', '{')):
    #     # Remove this after fixing linecache
    #     lines[line_number] = stripped_line
    #     return lines

    # The given line is a multiline comment
    if stripped_line.startswith('/*'):  # Maybe only `/* in taget_line`

        while '*/' not in lines[line_number].strip():
            del lines[line_number]
        del lines[line_number]
        return check_line(lines, line_number)

    # The given line is an annotation or one line comment.
    # We probably don't need this anymore, especially the // case.
    elif stripped_line.startswith(('@', '//')):

        del lines[line_number]
        return check_line(lines, line_number)

    # If the line is empty
    elif not stripped_line:

        del lines[line_number]
        # print(lines, line_number)
        return check_line(lines, line_number)

    else:
        # (target_line.startswith('.')
        #             or stripped_line.startswith(',')
        #             or prev_line.endswith(',')
        #             or prev_line.endswith('(')
        #             or stripped_line.startswith('new')
        #             # TODO: Remove all these conditions and do this for all lines to see what will happen!
        #             # Put it after other conditions and delete the last one.
        #         ):

        new_lines = lines[:]

        new_line = stripped_line
        i = line_number - 1

        while not prev_line.endswith((';', '{')):
            new_line = prev_line + ' ' + new_line
            new_lines[i] = ''
            i -= 1
            prev_line = re.sub(multi_comment, '', new_lines[i]).strip()
            prev_line = re.sub(single_comment, '', new_lines[i]).strip()

            # print('###################')

        # We also need to go down if it's a middle line
        while not stripped_line.endswith((';', '{')):  # Add { too like below

            # print('###################')

            if stripped_line.endswith('}'):
                # We were probably in an enum construct
                return lines

            del new_lines[line_number]
            stripped_line = re.sub(
                multi_comment, '', new_lines[line_number]).strip()
            stripped_line = re.sub(
                single_comment, '', new_lines[line_number]).strip()
            new_line += f' {stripped_line}'

        del new_lines[line_number]
        new_line = re.sub(multi_comment, '', new_line).strip()
        new_lines.insert(line_number, new_line)
        return new_lines

    # Statement may expand on multiple lines below
    # else:
    #     new_line = ''
    #     new_lines = lines[:]
    #     while not stripped_line.endswith((';', '{')):

    #         if stripped_line.endswith('}'):
    #             # We were probably in an enum construct
    #             return lines

    #         new_line += f' {stripped_line}'
    #         del new_lines[line_number]
    #         stripped_line = re.sub(
    #             multi_comment, '', new_lines[line_number]).strip()
    #         stripped_line = re.sub(
    #             single_comment, '', new_lines[line_number]).strip()

    #     # Appending the last matched line
    #     new_line += f' {stripped_line}'
    #     del new_lines[line_number]

    #     new_lines.insert(line_number, new_line)
    #     return new_lines


def test():

    # FIXME: Write proper tests!

    test_data = Path('./normalize_tests')

    # line_number = 24
    # with open(test_data/'AssertionTask.java') as f:
    #     lines = f.read().splitlines()

    # line_number = 25
    # with open(test_data/'LocalizedMessage.java') as f:
    #     lines = f.read().splitlines()

    # line_number = 194
    # with open(test_data/'RolesTest.java') as f:
    #     lines = f.read().splitlines()

    # line_number = 369
    # with open(test_data/'XdocsPagesTest.java') as f:
    #     lines = f.read().splitlines()

    # line_number = 36
    # with open(test_data/'InputIndentationCorrect.java') as f:
    #     lines = f.read().splitlines()

    # line_number = 31
    # with open(test_data/'SecureServiceTaskBaseTest.java') as f:
    #     lines = f.read().splitlines()

    # Enum
    # line_number = 35
    # with open(test_data/'WaitForTaskToComplete.java') as f:
    #     lines = f.read().splitlines()

    # line_number = 31
    # with open(test_data/'DefaultManagementMBeanAssembler.java') as f:
    #     lines = f.read().splitlines()

    # line_number = 155
    # with open(test_data/'TokenizerBenchmarkTestCase.java') as f:
    #     lines = f.read().splitlines()

    # line_number = 96
    # with open(test_data/'WebExtension.java') as f:
    #     lines = f.read().splitlines()

    # line_number = 366
    # with open(test_data/'NERCombinerAnnotator.java') as f:
    #     lines = f.read().splitlines()

    # line_number = 196
    # with open(test_data/'TokenizerBenchmarkTestCase.java') as f:
    #     lines = f.read().splitlines()

    # line_number = 81
    # with open(test_data/'AsyncCacheRequestManager.java') as f:
    #     lines = f.read().splitlines()

    # line_number = 166
    # with open(test_data/'SuppressWarningsHolder.java') as f:
    #     lines = f.read().splitlines()

    line_number = 97
    with open(test_data/'Qt5CPPGenerator.java') as f:
        lines = f.read().splitlines()

    # FIXME: These two break the regex and keeps the code in a loop
    # line_number = 71
    # with open(test_data/'PorterDuff.java') as f:
    #     lines = f.read().splitlines()
    # line_number = 175
    # with open(test_data/'Cipher.java') as f:
    #     lines = f.read().splitlines()

    new_lines = check_line(lines, line_number - 1)
    print(new_lines[line_number - 1])
    with open(test_data / 'Fixed.java', 'w') as f:
        f.write('\n'.join(new_lines))


def main():

    # import sys
    # test()
    # sys.exit(0)

    data_path = Path('../_data')
    # bugs_files = Path('../bugs_files')
    bugs_files = Path('../bugged_files')
    # output_dir = Path('./input')
    output_dir = Path('./input_large')

    bugs = bugs_reader.get_bugs(data_path / 'sstubsLarge.json')

    for bug in bugs:
        # user, repo, fix_commit, fix_commit_parent, file_path, bug_line_number, fix_line_number = get_info(
        #     bug)

        split_path = bug.bug_file_path.split('/')
        save_dir = '.'.join(split_path[:-1])
        file_name = split_path[-1]

        for type, commit, line_number in [('bug', bug.fix_commit_parent_sha1, bug.bug_line_num),
                                          ('fix', bug.fix_commit_sha1, bug.fix_line_num)]:
            # print(commit)
            pfile = Path(
                f'{bug.username}/{bug.repository}/{commit}/{save_dir}/{file_name}')
            output = (output_dir / pfile / f'{line_number}')

        # buggy_file = Path(
        #     f'{user}/{repo}/{fix_commit_parent}/{save_dir}/{file_name}')
        # fixed_file = Path(
        #     f'{user}/{repo}/{fix_commit}/{save_dir}/{file_name}')

        # output1 = (output_dir / buggy_file / f'{bug_line_number}')
        # output2 = (output_dir / fixed_file / f'{fix_line_number}')

            if not output.exists():

                with open(bugs_files / pfile) as f:
                    lines = f.read().splitlines()

                # ast_content = None
                # if type == 'bug':
                #     ast_content = lines[bug.bug_node_start_char:
                #                         bug.bug_node_start_char + bug.bug_node_length]
                # else:
                #     ast_content = lines[bug.fix_node_start_char:
                #                         bug.fix_node_start_char + bug.fix_node_length]

                # multiline = len(ast_content.splitlines()) > 1

                print(pfile, line_number)

                try:
                    normalized_lines = check_line(lines, line_number - 1)
                except:
                    # Because some line numbers are wrong in the dataset
                    # Example: https://github.com/JetBrains/intellij-community/commit/1876ac4a290bfeb7a4321c3232169dabd97367cf/source/com/intellij/lexer/__XmlLexer.java
                    # with fixline of 824
                    print(pfile, line_number)
                    continue

                output.mkdir(parents=True, exist_ok=True)
                with open(output / file_name, 'w') as f:
                    f.write('\n'.join(normalized_lines))


if __name__ == '__main__':
    main()
