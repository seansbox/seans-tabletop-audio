from invoke import task
import re
from download_file import download_file

@task
def build_public(c, pubdir="../public"):
  site = "https://cdn.jsdelivr.net/npm"

  download_file(c, f"{site}/@forevolve/bootstrap-dark@latest/dist/css/toggle-bootstrap.min.css", f"{pubdir}/css")
  download_file(c, f"{site}/@forevolve/bootstrap-dark@latest/dist/css/toggle-bootstrap-dark.min.css", f"{pubdir}/css")
  download_file(c, f"{site}/@forevolve/bootstrap-dark@latest/dist/css/toggle-bootstrap-print.min.css", f"{pubdir}/css")

  download_file(c, f"{site}/@forevolve/bootstrap-dark@latest/dist/js/bootstrap.bundle.min.js", f"{pubdir}/js")
  download_file(c, f"{site}/@forevolve/bootstrap-dark@latest/dist/js/bootstrap.bundle.min.js.map", f"{pubdir}/js")

  download_file(c, f"{site}/jquery@latest/dist/jquery.min.js", f"{pubdir}/js")
  download_file(c, f"{site}/jquery@latest/dist/jquery.min.map", f"{pubdir}/js")

  download_file(c, f"{site}/handlebars@latest/dist/handlebars.min.js", f"{pubdir}/js")
