import re
import glob
from invoke import task
from .print_progress import print_progress


@task
def replace_bulk(c, file_pattern, from_pattern, to_replacement):
    """
    Performs a regex-based find-and-replace operation in files matching a glob pattern.

    Parameters:
        file_pattern (str): Glob pattern to match files in which to perform the replacement.
        from_pattern (str): The regex pattern to search for.
        to_replacement (str): The string to replace each match with.
    """
    # Find all files matching the glob pattern
    files = glob.glob(file_pattern)
    total_files = len(files)

    for i, file in enumerate(files, start=1):
        print_progress(f"Replacing {file}", processed=i, total=total_files)

        # Read the file contents
        with open(file, "r") as f:
            content = f.read()

        # Perform the regex replacement
        updated_content = re.sub(from_pattern, to_replacement, content)

        # Write the updated content back to the file
        with open(file, "w") as f:
            f.write(updated_content)
