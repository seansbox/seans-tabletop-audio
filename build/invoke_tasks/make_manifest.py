from invoke import task
import json
import os
from .print_progress import print_progress  # Assuming print_progress is in a module


@task
def make_manifest(c, dir, output_file, manifest_func=None):
    dir = os.path.normpath(os.path.expanduser(dir))
    total_files = sum(len(files) for _, _, files in os.walk(dir))
    processed_files = 0

    def recurse_directory(dir):
        nonlocal processed_files
        dir_structure = {}
        # Sort entries alphabetically
        entries = sorted(os.listdir(dir))
        for entry in entries:
            entry_path = os.path.join(dir, entry)
            if os.path.isdir(entry_path):
                # Recursively process directories
                dir_structure[entry] = recurse_directory(entry_path)
            else:
                processed_files += 1
                if entry[0] == ".":
                    continue
                print_progress(f"Manifesting {entry}...", processed_files, total_files, 100)
                dir_structure[entry] = manifest_func(entry_path) if manifest_func else None
        return dir_structure

    # Build the structure starting from the root directory
    with open(output_file, "w") as f:
        json.dump(recurse_directory(dir), f, indent=2, sort_keys=True)
