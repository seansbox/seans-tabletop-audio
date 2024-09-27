import os
import re
import json
import logging
import urllib.error

import get
import html

htmlfile = get.read("index.html")
dictfile = get.read("dictionary_a.js")
listfile = get.read("tta4.js")

# Parse the HTML for the main media objects

media = {}

for song in re.split(r"<!--song", htmlfile):
    title = re.search(r'<div class="track_title"><h3 class = "(white|yellow)">(.*?)</', song)
    type = re.search(r'<span style="display:block;">\.?<i class = "(white|yellow)">(.*?)</', song)
    flavor = re.search(r'<span class="(white|yellow) flavor">(.*?)[\.\[<]', song)
    image = re.findall(r'<img data-src="(.*?)"', song)
    file = re.search(r"saveAs\('(.*?)'\)", song)
    if not title:
        continue
    title = title.group(2)
    # print(title, found)
    if not type:
        logging.warning(f"Warning: type missing from {title}")
        type = ""
    else:
        type = type.group(2)
    if not flavor:
        logging.warning(f"Warning: flavor missing from {title}")
        flavor = ""
    else:
        flavor = re.sub(r"\[.*?\]", "", flavor.group(2)).strip()
    if not image:
        logging.error(f"Error: image missing from {title}")
        exit(1)
    else:
        image = image[-1]
    if not file:
        logging.warning(f"Warning: file missing from {title}")
        continue
    else:
        file = file.group(1)
    num = file.split("_")[0]
    ttdatum = {
        "num": num,
        "title": title.replace(":", ": ").replace("  ", " "),
        "type": type,
        "flavor": flavor,
        "image": image,
        "file": file,
    }
    media[ttdatum["num"]] = ttdatum

    fname = ttdatum["image"].split("/")[-1].replace("%20", "-")
    get.download(ttdatum["image"], os.path.join("..", "images", fname), update=True)
    ttdatum["image"] = fname

# Clean up orphaned image files

images_new = [m["image"] for m in media.values()]
images_old = os.listdir(os.path.join("..", "images"))
images_del = [i for i in images_old if i not in images_new]
if len(images_del) < 10:
    for image in images_del:
        if image != ".gitignore":
            os.unlink(os.path.join("..", "images", image))

# Parse, combine, and download titles and sound files from tta4.js

# {title:"The Inner Core",artist:e,mp3:t+"1_The_Inner_Core.mp3"}
for match in re.findall(r'{title:"([^"]+?)"[^"]+?"([^"]+?)"}', listfile):
    if not ".mp3" in match[1]:
        continue
    song = media[match[1].split("_")[0]]
    if song["title"] != match[0]:
        if len(song["title"]) < len(match[0]):
            song["title"] = match[0]
    if song["file"] + ".mp3" != match[1]:
        logging.warning(f'Warning: file {song["file"]} mismatches {match[1]}')
    song["file"] = match[1]
    url = "https://sounds.tabletopaudio.com/" + match[1]
    print(url)
    try:
        get.download(url, os.path.join("..", "sounds", match[1]), update=True)
    except urllib.error.HTTPError as e:
        print(e)
        song["error"] = True

# Parse and append tags to media objects

# "350": ["spy","espionage","city","urban","stakeout","noir","street"]
for match in re.findall(r'"(.+?)" ?: \[(.+?)\]', dictfile):
    tags = match[1].split(",")
    tags = [s.replace('"', "") for s in tags]
    if match[0] in media:
        media[match[0]]["tags"] = tags
        # Opinionated adjustment...
        if "combat" in tags:
            tags.append("initiative")  # so we can search for it
            media[match[0]]["color"] = "#FF9999"
    else:
        logging.warning(f'Warning: song "{match[0]}" missing for tagging')

for song in media.values():
    if not "tags" in song:
        logging.warning(f'Warning: "{song["title"]}" missing tags')
    if "error" in song:
        logging.warning(f'Warning: "{song["title"]}" has a download error')

# Sort the media and add on the paths
media = sorted(media.values(), key=lambda d: d["title"])
for med in media:
    med["file"] = f"sounds/{med['file']}"
    med["image"] = f"images/{med['image']}"
    med["num"] = int(med["num"])

foundry = {
    "name": "Tabletop Audio",
    "description": "Songs imported from www.tabletopaudio.com",
    "fade": 3000,
    "folder": None,
    "mode": 0,
    "playing": False,
    "sorting": "a",
    "sounds": [],
}
for med in media:
    if "error" in med:
        continue
    foundry["sounds"].append(
        {
            "name": med["title"],  # str(med["num"]).zfill(3) + " " + med["title"],
            "description": med["flavor"],
            "path": "sounds/" + med["file"].split("/")[-1],
            "fade": 3000,
            "repeat": True,
            "volume": 0.8,
        }
    )

open("../index.html", "w", encoding="utf-8").write(html.render_html("Tabletop Audio", media))

# Manifest
# media = sorted(media, key=lambda d: d["title"])
manifest = {}
for med in media:
    if "error" in med:
        continue
    manifest[med["title"]] = med
    del manifest[med["title"]]["title"]

open("../public/js/manifest.js", "w", encoding="utf-8").write(
    "var manifest = " + json.dumps(manifest, indent=2, sort_keys=True)
)
open("manifest.json", "w", encoding="utf-8").write(json.dumps(foundry, indent=2))
