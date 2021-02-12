from pathlib import Path

# TODO: Make this a corruption test for downloaded data
p = Path('../bugs_files/')
java_files = p.glob('**/*.java')

for jfile in java_files:
    try:
        if jfile.is_file():
            with jfile.open() as jf:
                content = jf.read()
                lines = content.splitlines()
                ## Wrong new lines ##
                if all([lines[i] == '' for i in range(1, len(lines), 2)]):
                    print(jfile)
                # Empty download
                if 'not found' in lines[0].strip().lower():
                    print(jfile)
    except Exception as e:
        print(e)
        print(jfile)
