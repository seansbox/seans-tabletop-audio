#!/bin/bash
set -e  # exit on error
help() { echo "Usage: $0 {command} [args]"; echo "Commands:"; declare -F | awk '{print "  " $3}'; }

build() {
  #[ -z "$2" ] || [ -z "$3" ] && { echo "Usage: $0 build {thing} {stuff}"; exit 1; }
  curl -o "index.html" "https://tabletopaudio.com/index.html"
  curl -o "dictionary_a.js" "https://tabletopaudio.com/bootstrap/js/dictionary_a.js"
  curl -o "tta4.js" "https://tabletopaudio.com/bootstrap/js/tta4.js"
  python3 build.py
}

build_public() {
  sh web.sh build_libs
  sh web.sh build_fonts
  sh web.sh build_icon nf-seti-audio "#FFFFFF" "#F44336"
}

serve() {
  python3 -m http.server 8001 --directory ..
}

"${1:-help}" "$@"
