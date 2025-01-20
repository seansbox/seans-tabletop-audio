#!/bin/sh

set -e
PROJECT_NAME=$(basename "$(dirname "$(pwd)")")
USER_ID=$(id -u)
GROUP_ID=$(id -g)

run() {
    local FLAGS=""
    [ "$1" = "interactive" ] && FLAGS="-it" && shift
    docker run $FLAGS --rm -e HOME=/home -e PIPENV_CUSTOM_VENV_NAME=$PROJECT_NAME \
        --hostname $PROJECT_NAME -v dockbuilder:/home -v "$(pwd)/..:/app" dockbuilder sh -c "
        chown $USER_ID:$GROUP_ID /home && su-exec $USER_ID:$GROUP_ID \
        env HOME=/home PIPENV_CUSTOM_VENV_NAME=$PROJECT_NAME sh -c \"$1\""
}

if [ "$1" = "clean" ]; then
  docker rmi -f dockbuilder || true
  docker volume rm dockbuilder || true
exit; fi

docker volume create dockbuilder
docker build -t dockbuilder - <<EOF
FROM python:3-alpine
ENV PYTHONUNBUFFERED=1 LANG=C.UTF-8
RUN apk add --no-cache bash curl make nano nodejs npm p7zip su-exec wget \
    && pip install --no-cache-dir --upgrade pip pipenv invoke && npm update -g npm
WORKDIR /app/build
EOF

if [ "$1" = "shell" ]; then run interactive "/bin/bash"; exit; fi

run "pipenv install && pipenv run invoke $*"
