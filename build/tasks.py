import json
import re
import os

from invoke import task

from sync_symlink_folder import sync_symlink_folder
from download_file import download_file, download_font
from run_server import run_server
from build_public import build_public
from regex_replace import regex_replace
from build_favicon import build_favicon as build_favicon

import html

def read(file): return open(file, "r", encoding="utf-8").read()

@task(default=True)
def build(c):
    htmlfile = read(download_file(c, "https://tabletopaudio.com/index.html"))
    dictfile = read(download_file(c, "https://tabletopaudio.com/bootstrap/js/dictionary_a.js"))
    listfile = read(download_file(c, "https://tabletopaudio.com/bootstrap/js/tta4.js"))

    media = parse_media(htmlfile)
    download_images(c, media)
    download_sounds(c, media, listfile)
    add_tags(media, dictfile)
    foundry_data = build_foundry_data(media)
    write_manifest(media, foundry_data)

    download_font(c, "https://fonts.googleapis.com/css?family=Fira+Code:400,b,bi,i", "fira-code")
    download_font(c, "https://fonts.googleapis.com/css?family=Fira+Sans+Condensed:400,b,bi,i", "fira-sans-condensed")
    download_font(c, "https://fonts.googleapis.com/css?family=Noto+Emoji:400,b,bi,i", "noto-emoji")
    download_font(c, "https://fonts.googleapis.com/css?family=Amatic+SC:400,b,bi,i", "amatic-sc")
    download_font(c, "https://raw.githubusercontent.com/ryanoasis/nerd-fonts/master/css/nerd-fonts-generated.css", "nerd-font",
      fixfunc=lambda x: x.replace("../fonts/Symbols-2048-em Nerd Font Complete.woff2", "https://github.com/ryanoasis/nerd-fonts/raw/refs/heads/master/patched-fonts/NerdFontsSymbolsOnly/SymbolsNerdFont-Regular.ttf") )
    regex_replace(c, "../public/ttf/nerd-font/nerd-font.css", "woff2", "truetype")

    build_favicon(c, "nf-seti-audio", "#FFFFFF", "#F44336")

    sync_symlink_folder(c, srcdir="../raw/sounds", dstdir="../sounds")

def parse_media(htmlfile):
    media = {}
    for song in re.split(r"<!--song", htmlfile):
        title, type_, flavor, image, file = extract_song_data(song)
        if not title:
            continue
        media_entry = {
            "num": file.split("_")[0],
            "title": title.replace(":", ": ").replace("  ", " "),
            "type": type_,
            "flavor": flavor,
            "image": image[-1] if image else "",
            "file": file,
        }
        if not media_entry['num']:
            continue
        media[media_entry["num"]] = media_entry
    return media

def extract_song_data(song):
    title = re.search(r'<div class="track_title"><h3 class = "(white|yellow)">(.*?)</', song)
    type_ = re.search(r'<span style="display:block;">\.?<i class = "(white|yellow)">(.*?)</', song)
    flavor = re.search(r'<span class="(white|yellow) flavor">(.*?)[\.\[<]', song)
    image = re.findall(r'<img data-src="(.*?)"', song)
    file = re.search(r"saveAs\('(.*?)'\)", song)
    return (title.group(2) if title else None,
            type_.group(2) if type_ else "",
            re.sub(r"\[.*?\]", "", flavor.group(2)).strip() if flavor else "",
            image,
            f"{file.group(1)}.mp3" if file else "")

def download_images(c, media):
    for entry in media.values():
        if entry["image"]:
            filename = entry["image"].split("/")[-1].replace("%20", "-")
            if not os.path.isfile(f"../images/{filename}"):
              download_file(c, entry["image"], "../images", name=filename)
            entry["image"] = filename

def download_sounds(c, media, listfile):
    for title, path in re.findall(r'{title:"([^"]+?)"[^"]+?"([^"]+?)"}', listfile):
        if ".mp3" not in path:
            continue
        song = media.get(path.split("_")[0])
        if song and song["title"] != title:
            song["title"] = title if len(title) > len(song["title"]) else song["title"]
        url = "https://sounds.tabletopaudio.com/" + path
        try:
            if not os.path.isfile(f"../sounds/{path}"):
              print(f"Downloading ../sounds/{path}")
              download_file(c, url, "../sounds", name=path)
        except urllib.error.HTTPError as e:
            print(f'Warning: "{song["title"]}" download failed with error: {e}')
            song["error"] = True

def add_tags(media, dictfile):
    for num, tags in re.findall(r'"(.+?)" ?: \[(.+?)\]', dictfile):
        tags = [tag.strip('"') for tag in tags.split(",")]
        if num in media:
            media[num]["tags"] = tags
            if "combat" in tags:
                tags.append("initiative")
                media[num]["color"] = "#FF9999"
        else:
            print(f'Warning: song "{num}" missing for tagging')

def build_foundry_data(media):
    foundry_data = {
        "name": "Tabletop Audio",
        "description": "Songs imported from www.tabletopaudio.com",
        "fade": 3000,
        "folder": None,
        "mode": 0,
        "playing": False,
        "sorting": "a",
        "sounds": [],
    }
    for entry in sorted(media.values(), key=lambda e: e["title"]):
        if "error" not in entry:
            foundry_data["sounds"].append({
                "name": entry["title"],
                "description": entry["flavor"],
                "path": f"sounds/{entry['file'].split('/')[-1]}",
                "fade": 3000,
                "repeat": True,
                "volume": 0.8,
            })
    return foundry_data

def write_manifest(media, foundry_data):
    # Write HTML index
    with open("../index.html", "w", encoding="utf-8") as f:
        f.write(html.render_html("Tabletop Audio", media))

    # Write manifest files
    manifest_data = {entry["title"]: entry for entry in media.values() if "error" not in entry}
    for entry in manifest_data.values():
        del entry["title"]
    with open("../public/js/manifest.js", "w", encoding="utf-8") as f:
        f.write("var manifest = " + json.dumps(manifest_data, indent=2, sort_keys=True))
    with open("../manifest.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(foundry_data, indent=2))
