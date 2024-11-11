from invoke import task
from .print_progress import print_progress
from .delete_files import delete_files

import glob
import os
import zipfile
import shutil


@task
def unzip_files(c, pattern, dstdir="."):
    """
    Unzip files that match the given pattern into the specified destination folder.
    If the unzipped contents include a single folder with a name matching the zip file,
    the script will collapse it into the destination folder.
    """

    # Ensure the destination directory exists
    if not os.path.exists(dstdir):
        os.makedirs(dstdir, exist_ok=True)

    # Pre-collect files matching the pattern and count them
    zip_files = sorted([file for file in glob.glob(pattern) if file.endswith(".zip")])
    total_files = len(zip_files)

    # Process each zip file and show progress
    for i, file in enumerate(zip_files, 1):
        folder_name = os.path.basename(file).replace(".zip", "")
        folder = os.path.join(dstdir, folder_name)  # Destination folder

        if not os.path.exists(folder):
            print_progress(f"Unzipping {file} to {folder}...", processed=i, total=total_files, show_every=1)
            os.makedirs(folder, exist_ok=True)

            with zipfile.ZipFile(file, "r") as zip_ref:
                zip_ref.extractall(folder)
            if os.path.isdir(os.path.join(folder, "__MACOSX")):
                shutil.rmtree(os.path.join(folder, "__MACOSX"))
            if os.path.isfile(os.path.join(folder, ".DS_Store")):
                os.remove(os.path.join(folder, ".DS_Store"))

            # Check if the extracted folder contains a single subfolder
            extracted_items = os.listdir(folder)
            if len(extracted_items) == 1:
                single_subfolder = os.path.join(folder, extracted_items[0])
                if os.path.isdir(single_subfolder):
                    for item in os.listdir(single_subfolder):
                        shutil.move(os.path.join(single_subfolder, item), folder)
                    os.rmdir(single_subfolder)  # Remove the now-empty subfolder
