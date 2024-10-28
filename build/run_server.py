from invoke import task
import http.server
import socketserver

@task
def run_server(c, port=8001, directory=".."):
    """
    Start a simple HTTP server to serve files from a specified directory.

    Args:
        c (invoke.Context): The context instance (required by Invoke).
        port (int): The port number to serve on. Defaults to 8001.
        directory (str): The directory to serve files from. Defaults to the current directory.
    """
    class CustomHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=directory, **kwargs)

    with socketserver.TCPServer(("", port), CustomHandler) as httpd:
        print(f"Serving files from '{directory}' at http://localhost:{port}")
        httpd.serve_forever()
