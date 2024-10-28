import re
from invoke import task

@task
def regex_replace(c, file, from_pattern, to_replacement):
    """
    Performs a regex-based find-and-replace operation in a file.

    Parameters:
        file (str): Path to the file in which to perform the replacement.
        from_pattern (str): The regex pattern to search for.
        to_replacement (str): The string to replace each match with.
    """
    # Read the file contents
    with open(file, "r") as f:
        content = f.read()

    # Perform the regex replacement
    updated_content = re.sub(from_pattern, to_replacement, content)

    # Write the updated content back to the file
    with open(file, "w") as f:
        f.write(updated_content)
