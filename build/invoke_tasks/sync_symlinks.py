import os
import re
import shutil
from invoke import task
from .print_progress import print_progress

WORDS_TO_REMOVE = [
    "- $5 Rewards",
    "(Gridded Part 1)",
    "(Gridded Part 2)",
    "(Gridless Part 1)",
    "(Gridless Part 2)",
    "(Gridded Pt.1)",
    "(Gridded Pt.2)",
    "(Gridless Pt.1)",
    "(Gridless Pt.2)",
    "Pt 1",
    "Pt 2",
    "Pt 3",
    "Pt1",
    "Pt2",
    "Pt3",
    "Pt.1",
    "Pt.2",
    "Pt.3",
    "Pt. 1",
    "Pt. 2",
    "Pt. 3",
    "- Part 1",
    "- Part 2",
    "- Part 3",
    "Part 1",
    "Part 2",
    "Part 3",
    "- Gridless",
    "- Gridded",
    "(Gridded)",
    "(Gridless)",
    "Gridless",
    "Gridded",
]


def rename_func(relative_path):
    # Remove words from filename
    for word in WORDS_TO_REMOVE:
        relative_path = relative_path.replace(word, "")
    # Remove extra spaces and strip leading/trailing spaces
    relative_path = re.sub(r"\s+", " ", relative_path).strip()
    return relative_path


@task
def sync_symlinks(c, srcdir, dstdir, rename_func=None):
    """
    Synchronize symlinks in the target directory, mirroring the folder structure of the source directory.

    For each file in `srcdir`, a corresponding symlink is created in `dstdir`. If files are removed from `srcdir`,
    corresponding symlinks in `dstdir` will be removed as well.

    Parameters:
        - srcdir (str): Directory containing the source files.
        - dstdir (str): Directory where symlinks will be created.
        - rename_func (callable, optional): Function that takes a relative path (from srcdir) and returns a new relative path.
    """
    # Count total files to show the progress more effectively
    total_files = sum(len(files) for _, _, files in os.walk(srcdir))
    processed_files = 0
    created_symlinks = set()  # Track valid symlink paths for cleanup

    # Create directories and symlinks, and remove any .DS_Store files
    for root, dirs, files in os.walk(srcdir):
        for file in files:
            source_file = os.path.join(root, file)

            # Skip unwanted files
            if file in {".DS_Store", "desktop.ini"} or file.startswith("."):
                continue

            processed_files += 1

            # Compute relative path from srcdir to source_file
            relative_file_path = os.path.relpath(source_file, srcdir)

            # Apply rename_func to relative_file_path
            new_relative_path = rename_func(relative_file_path) if rename_func else relative_file_path
            if new_relative_path is None:
                continue

            # Construct the target file path
            target_file = os.path.normpath(os.path.join(dstdir, new_relative_path))

            # Ensure the target directory exists
            target_dir = os.path.dirname(target_file)
            if not os.path.exists(target_dir):
                os.makedirs(target_dir, exist_ok=True)

            # Compute the relative source path for the symlink
            rel_source = os.path.relpath(source_file, os.path.dirname(target_file))

            print_progress(f"Symlinking {file}...", processed_files, total_files, 100)

            # Only recreate symlink if it doesn't exist or points to the wrong target
            if os.path.islink(target_file):
                if os.readlink(target_file) != rel_source:
                    os.remove(target_file)
                    os.symlink(rel_source, target_file)
            else:
                os.symlink(rel_source, target_file)

            # Track this symlink path as valid
            created_symlinks.add(target_file)

    print_progress("Removing orphaned symlinks...")

    # Remove symlinks in the target directory that no longer have corresponding files in the source
    for root, dirs, files in os.walk(dstdir, topdown=False):
        for file in files:
            target_file = os.path.normpath(os.path.join(root, file))
            # Remove symlinks that are not in the created_symlinks set
            if target_file not in created_symlinks:
                os.remove(target_file)

        # Remove empty directories in the target that no longer exist in the source
        for dir in dirs:
            target_subdir = os.path.normpath(os.path.join(root, dir))
            if os.path.isdir(target_subdir) and not os.listdir(target_subdir):
                shutil.rmtree(target_subdir, ignore_errors=True)
