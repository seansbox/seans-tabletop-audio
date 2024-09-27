import os
from urllib.request import urlopen, Request
from urllib.parse import unquote
import logging

import ssl

ssl._create_default_https_context = ssl._create_unverified_context


def read(file):
    f = open(file, "r", encoding="utf-8")
    data = f.read()
    f.close()
    return data


# utility function for downloading files
def download(url, file=None, folder=None, read=False, update=False):
    if folder and not os.path.exists(folder):
        os.makedirs(folder)
    if not file:
        file = unquote(url.split("/")[-1])
    if folder:
        file = os.path.join(folder, file)
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
    }
    if not update or not os.path.exists(file):
        logging.info(f"Downloading {url}...")
        r = urlopen(Request(url, headers=headers)).read()
        open(file, "wb").write(r)
    if read:
        return read(file)
    else:
        return file
