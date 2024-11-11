import re
import os
import ssl
import urllib.request
from urllib.error import URLError, HTTPError
from invoke import task

USER_AGENTS = {
    "eot": "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0; GTB7.4; InfoPath.2; SV1; .NET CLR 3.3.69573; WOW64; en-US)",
    "woff2": "Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0",
    "woff": "Mozilla/5.0 (compatible, MSIE 11, Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko",
    "ttf": "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; de-at) AppleWebKit/533.21.1 (KHTML, like Gecko) Version/5.0.5 Safari/533.21.1",
    "svg": "Mozilla/5.0(iPad; U; CPU iPhone OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B314 Safari/531.21.10gin_lib.cc",
}

UNVERIFIED_SSL_CONTEXT = ssl._create_unverified_context()


@task
def download_file(c, url, dir=os.getcwd(), name=None, user_agent=USER_AGENTS["ttf"]):
    """
    Download a file from a URL, ignoring SSL verification and setting a custom User-Agent.

    Parameters:
        c (invoke.Context): Context instance (required by the @task decorator).
        url (str): URL of the file to download.
        dir (str, optional): Destination directory for the downloaded file. Defaults to the current working directory.
        name (str, optional): Destination file name for the downloaded file. If not provided, the file name is derived from the URL.
        user_agent (str, optional): User-Agent string to mimic a specific browser. Defaults to USER_AGENTS['ttf'].

    Returns:
        str: The path of the downloaded file.
    """
    # Default destination to the current working directory with the filename from the URL
    dest = os.path.join(dir, name or os.path.basename(url))

    # Setup request with custom headers
    headers = {"User-Agent": user_agent}
    req = urllib.request.Request(url, headers=headers)

    with urllib.request.urlopen(req, context=UNVERIFIED_SSL_CONTEXT) as response:
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "wb") as file:
            file.write(response.read())
    return dest


@task
def download_font(c, url, slug, dir="../public/ttf", fixfunc=None, user_agent=USER_AGENTS["ttf"]):
    """
    Download and process a font CSS file and its font files, with optional path fixing for font URLs.

    Parameters:
        c (invoke.Context): Context instance (required by the @task decorator).
        url (str): URL to the CSS file that defines the font styles.
        slug (str): Name of the font, used to create a directory and file names.
        dir (str, optional): Base directory to store downloaded fonts and CSS files.
        fixfunc (function, optional): A function to modify each font URL before downloading. It should accept a URL string and return the modified URL.

    Returns:
        None
    """
    css_path = f"{dir}/{slug}"
    download_file(c, url, css_path, name=f"{slug}.css", user_agent=user_agent)

    # Extract URLs from CSS and download each font file
    css_file_path = f"{css_path}/{slug}.css"
    with open(css_file_path, "r") as css_file:
        css_content = css_file.read()
        # Updated pattern to exclude any leading or trailing quotes around the URL
        font_urls = re.findall(r'url\([\'"]?([^\'")]+)[\'"]?\)', css_content)
        for font_url in font_urls:
            if fixfunc:
                font_url_fixed = fixfunc(font_url)
                css_content = css_content.replace(font_url, font_url_fixed.split("/")[-1])
                font_url = font_url_fixed
            else:
                css_content = css_content.replace(font_url, font_url.split("/")[-1])
            download_file(c, font_url, css_path, user_agent=user_agent)

    with open(css_file_path, "w") as css_file:
        css_file.write(css_content)
