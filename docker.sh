docker run -it --rm -v "$(pwd)":/workspace -w /workspace python:3-alpine sh -c "apk add --no-cache nano && pip install invoke pillow && sh"
