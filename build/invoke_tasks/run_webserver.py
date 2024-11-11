from invoke import task
import os
import http.server
import socketserver


@task
def run_webserver(c, port=8001, dir=os.getcwd()):
    """
    Start a simple HTTP server to serve files from a specified directory.

    Args:
        c (invoke.Context): The context instance (required by Invoke).
        port (int): The port number to serve on. Defaults to 8001.
        dir (str): The directory to serve files from. Defaults to the current directory.
    """

    class CustomHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, dir=dir, **kwargs)

    with socketserver.TCPServer(("", port), CustomHandler) as httpd:
        print(f"Serving files from '{dir}' at http://localhost:{port}")
        httpd.serve_forever()
