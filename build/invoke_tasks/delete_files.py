from invoke import task
import glob
import os
import shutil
from .print_progress import print_progress


@task
def delete_files(c, pattern):
    """
    Delete files and folder trees that match a specified glob pattern, with progress indication.

    Args:
        c: Context (required by invoke, even if not used here).
        pattern (str): Glob pattern to match files or folders (e.g., "*.txt" or "folder/*").
    """
    paths_to_delete = glob.glob(pattern, recursive=True)
    total_files = len(paths_to_delete)

    for i, path in enumerate(paths_to_delete, start=1):
        if os.path.isfile(path):
            message = f"Deleting file {path}"
        elif os.path.isdir(path):
            message = f"Deleting folder {path}"
        print_progress(message, processed=i, total=total_files)
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)
