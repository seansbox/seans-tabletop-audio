import os
import shutil
from invoke import task
from print_progress import print_progress


# Function to compute relative path from one directory to another
def relative_path(source, target):
    return os.path.relpath(source, os.path.dirname(target))


@task
def sync_symlinks(c, srcdir, dstdir):
    """
    Synchronize symlinks in the target directory, mirroring the folder structure of the source directory.

    For each file in `srcdir`, a corresponding symlink is created in `dstdir`. If files are removed from `srcdir`,
    corresponding symlinks in `dstdir` will be removed as well.

    Parameters:
        - srcdir (str): Directory containing the source files.
        - dstdir (str): Directory where symlinks will be created.
    """
    # Count total files to show the progress more effectively
    total_files = sum(len(files) for _, _, files in os.walk(srcdir))
    processed_files = 0

    # Create directories and symlinks, and remove any .DS_Store files
    for root, dirs, files in os.walk(srcdir):

        # Re-create directories in the target
        relative_dir = os.path.relpath(root, srcdir)
        target_dir = os.path.join(dstdir, relative_dir)

        if not os.path.exists(target_dir):
            os.makedirs(target_dir, exist_ok=True)

        # Create symlinks for each file, excluding .DS_Store
        for file in files:
            processed_files += 1
            # Remove any .DS_Store files found in the source
            if file == ".DS_Store" or file == "desktop.ini":
                os.remove(os.path.join(root, ".DS_Store"))
            elif file.startswith("."):
                continue

            source_file = os.path.join(root, file)
            target_file = os.path.join(target_dir, file)
            rel_source = relative_path(source_file, target_file)

            # Only recreate symlink if it doesn't exist or points to the wrong target
            if os.path.islink(target_file):
                if os.readlink(target_file) != rel_source:
                    os.remove(target_file)
                    os.symlink(rel_source, target_file)
            else:
                os.symlink(rel_source, target_file)

            # Update progress after each file
            print_progress(processed_files, total_files)

    # Remove symlinks in the target directory that no longer have corresponding files in the source
    for root, dirs, files in os.walk(dstdir, topdown=False):
        relative_dir = os.path.relpath(root, dstdir)
        source_dir = os.path.join(srcdir, relative_dir)

        # Remove symlinks for files that no longer exist in the source
        for file in files:
            target_file = os.path.join(root, file)
            source_file = os.path.join(source_dir, file)

            if not os.path.exists(source_file) or file.startswith(".DS") or file.startswith(".git"):
                os.remove(target_file)

        # Remove empty directories in the target that no longer exist in the source
        for dir in dirs:
            target_subdir = os.path.join(root, dir)
            source_subdir = os.path.join(source_dir, dir)

            if not os.path.exists(source_subdir) or file.startswith(".DS") or file.startswith(".git"):
                shutil.rmtree(target_subdir, ignore_errors=True)
