#!/bin/bash
set -e  # exit on error
help() { echo "Usage: $0 {command} [args]"; echo "Commands:"; declare -F | awk '{print "  " $3}' | grep -v '^  _'; }

# Define directories
CSS="../public/css"
JS="../public/js"
ICO="../public/ico"
TTF="../public/ttf"

# Define user agents for different font formats
EOT_AGENT="Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0; GTB7.4; InfoPath.2; SV1; .NET CLR 3.3.69573; WOW64; en-US)"
WOFF2_AGENT="Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0"
WOFF_AGENT="Mozilla/5.0 (compatible, MSIE 11, Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko"
TTF_AGENT="Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; de-at) AppleWebKit/533.21.1 (KHTML, like Gecko) Version/5.0.5 Safari/533.21.1"
SVG_AGENT="Mozilla/5.0(iPad; U; CPU iPhone OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B314 Safari/531.21.10gin_lib.cc"

build_libs() {
  mkdir -p "$CSS"
  curl -o "$CSS/toggle-bootstrap.min.css" "https://cdn.jsdelivr.net/npm/@forevolve/bootstrap-dark@latest/dist/css/toggle-bootstrap.min.css"
  curl -o "$CSS/toggle-bootstrap-dark.min.css" "https://cdn.jsdelivr.net/npm/@forevolve/bootstrap-dark@latest/dist/css/toggle-bootstrap-dark.min.css"
  curl -o "$CSS/toggle-bootstrap-print.min.css" "https://cdn.jsdelivr.net/npm/@forevolve/bootstrap-dark@latest/dist/css/toggle-bootstrap-print.min.css"

  mkdir -p "$JS"
  curl -o "$JS/bootstrap.bundle.min.js" "https://cdn.jsdelivr.net/npm/@forevolve/bootstrap-dark@latest/dist/js/bootstrap.bundle.min.js"
  curl -o "$JS/bootstrap.bundle.min.js.map" "https://cdn.jsdelivr.net/npm/@forevolve/bootstrap-dark@latest/dist/js/bootstrap.bundle.min.js.map"
  curl -o "$JS/jquery.min.js" "https://cdn.jsdelivr.net/npm/jquery@latest/dist/jquery.min.js"
  curl -o "$JS/jquery.min.map" "https://cdn.jsdelivr.net/npm/jquery@latest/dist/jquery.min.map"
  curl -o "$JS/handlebars.min.js" "https://cdn.jsdelivr.net/npm/handlebars@latest/dist/handlebars.min.js"
}

_build_font() {
  FOLDER="$1"
  CSSPATH="$2"
  RELPATH="${3:-}"

  mkdir -p "$TTF/$FOLDER" && pushd "$TTF/$FOLDER"
  curl -A "$TTF_AGENT" -o "../$FOLDER.css" "$CSSPATH"
  grep -oE 'url\([^)]+\)' "../$FOLDER.css" | sed 's/url(//g' | sed 's/)//g' | xargs -I {} curl -O "$RELPATH{}"
  sed -i.bak -E "s|url\(.*\/([^/\)]+)\)|url($FOLDER/\1)|g" "../$FOLDER.css" && rm ../*.bak
  tr '\n' '~' < "../$FOLDER.css" | sed 's|{~|{ |g' | sed 's|~}| }|g' | sed 's|\t|  |g' | sed 's|  | |g' | sed 's|  | |g' | tr '~' '\n' > temp.css && mv temp.css "../$FOLDER.css"
  popd
}

_build_font_nerd() {
  mkdir -p "$TTF/nerd-font" && pushd "$TTF/nerd-font"
  curl -A "$TTF_AGENT" -o "../nerd-font.css" "https://raw.githubusercontent.com/ryanoasis/nerd-fonts/master/css/nerd-fonts-generated.css"
  curl -o "nerd-font.ttf" "https://raw.githubusercontent.com/ryanoasis/nerd-fonts/master/patched-fonts/NerdFontsSymbolsOnly/SymbolsNerdFontMono-Regular.ttf"
  sed -i.bak -E 's|url\(.*\) format\(.*\)|url("nerd-font/nerd-font.ttf") format("truetype")|g' "../nerd-font.css" && rm ../*.bak
  tr '\n' '~' < "../nerd-font.css" | sed 's|{~|{ |g' | sed 's|~}| }|g' | sed 's|\t|  |g' | sed 's|  | |g' | sed 's|  | |g' | tr '~' '\n' > temp.css && mv temp.css "../nerd-font.css"
  popd
}

build_fonts() {
  _build_font "fira-sans-condensed" "https://fonts.googleapis.com/css?family=Fira+Sans+Condensed:400,b,bi,i"
  _build_font "amatic-sc" "https://fonts.googleapis.com/css?family=Amatic+SC:400,b,bi,i"
  _build_font "noto-emoji" "https://fonts.googleapis.com/css?family=Noto+Emoji:400,b,bi,i"
  _build_font "game-icons" "https://raw.githubusercontent.com/seansbox/gameicons-xlsx/main/game-icons.css" "https://raw.githubusercontent.com/seansbox/gameicons-xlsx/main/"
  _build_font_nerd
}

# Function to extract the symbol from CSS and create a temporary symbol text file
_build_icon_symbol() {
  local SYMBOLNAME="$1"
  local CSSFILE="$2"
  perl -CS -ne '/\.'${SYMBOLNAME}':before { content: "\\([^"]+)"/ and print chr(hex($1))' "$CSSFILE" > temp-symbol.txt
}

# Function to create touch icons
_build_icon_touch() {
  local SYMBOL="$1"
  local FG="$2"
  local BG="$3"
  local TTFFILE="$4"
  magick -background none -fill "$FG" -font "$TTFFILE" -pointsize 768 label:"$SYMBOL" temp-symbol.png
  magick -size 1024x1024 xc:"$BG" temp-background.png
  magick temp-background.png temp-symbol.png -gravity center -composite temp-touch.png
  for size in 57 72 114 120 144 152; do
      magick temp-touch.png -resize "${size}x${size}" -filter point "$ICO/apple-touch-icon-${size}x${size}.png"
  done
}

# Function to create favicons
_build_icon_fav() {
  local SYMBOL="$1"
  local FG="$2"
  local BG="$3"
  local TTFFILE="$4"
  magick -background none -fill "$FG" -font "$TTFFILE" -pointsize 576 label:"$SYMBOL" temp-symbol.png
  magick -size 1024x1024 xc:none -fill "$BG" -draw "circle 512,512 512,64" temp-background.png
  magick temp-background.png temp-symbol.png -gravity center -composite temp-favicon.png
  magick temp-favicon.png -resize 16x16 -filter point "$ICO/favicon-16x16.png"
  magick temp-favicon.png -resize 32x32 -filter point "$ICO/favicon-32x32.png"
  magick temp-favicon.png -define icon:auto-resize=64,48,32,16 "$ICO/favicon.ico"
}

# Function to create tile icons
_build_icon_tile() {
  local SYMBOL="$1"
  local FG="$2"
  local BG="$3"
  local TTFFILE="$4"
  magick -background none -fill "$FG" -font "$TTFFILE" -pointsize 108 label:"$SYMBOL" temp-symbol.png
  magick -size 144x144 xc:none temp-background.png
  magick temp-background.png temp-symbol.png -colorspace RGB -gravity center -composite "$ICO/mstile-144x144.png"
}

# Main function to build icons
build_icon() {
  [ -z "$2" ] || [ -z "$3" ] || [ -z "$4" ] && { echo "Optional: $0 build-icon {symbol} {fgcolor} {bgcolor}"; }
  local NF="${2:-nf-seti-audio}"
  local FG="${3:-#FFFFFF}"
  local BG="${4:-#F44336}"

  mkdir -p "$ICO"

  # Generate the favicon HTML links
  cat <<EOF > "$ICO/favicon.html"
<link rel="shortcut icon" href="$ICO/favicon.ico">
<link rel="icon" sizes="32x32" href="$ICO/favicon-32x32.png" />
<link rel="icon" sizes="16x16" href="$ICO/favicon-16x16.png" />
<link rel="apple-touch-icon-precomposed" sizes="57x57" href="$ICO/apple-touch-icon-57x57.png" />
<link rel="apple-touch-icon-precomposed" sizes="72x72" href="$ICO/apple-touch-icon-72x72.png" />
<link rel="apple-touch-icon-precomposed" sizes="114x114" href="$ICO/apple-touch-icon-114x114.png" />
<link rel="apple-touch-icon-precomposed" sizes="120x120" href="$ICO/apple-touch-icon-120x120.png" />
<link rel="apple-touch-icon-precomposed" sizes="144x144" href="$ICO/apple-touch-icon-144x144.png" />
<link rel="apple-touch-icon-precomposed" sizes="152x152" href="$ICO/apple-touch-icon-152x152.png" />
<meta name="msapplication-TileColor" content="$BG" />
<meta name="msapplication-TileImage" content="$ICO/mstile-144x144.png" />
EOF

  _build_icon_symbol "$NF" "$TTF/nerd-font.css"
  _build_icon_touch "$(cat temp-symbol.txt)" "$FG" "$BG" "$TTF/nerd-font/nerd-font.ttf"
  _build_icon_fav "$(cat temp-symbol.txt)" "$FG" "$BG" "$TTF/nerd-font/nerd-font.ttf"
  _build_icon_tile "$(cat temp-symbol.txt)" "$FG" "$BG" "$TTF/nerd-font/nerd-font.ttf"
  rm temp-*.*
}

"${1:-help}" "$@"
