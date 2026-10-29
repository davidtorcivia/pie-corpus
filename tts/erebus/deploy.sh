#!/bin/sh
# Build and run the PIE pitch-patched Kokoro service on erebus (docs/pronunciation.md "Deployment on erebus").
# Run from the Mac, in the repo:   sh tts/erebus/deploy.sh [deploy|start|stop|restart|status|logs|remove]
#
# Touches only: the directory ~/pie-tts/ (the build context), the image pie-tts:* and the container pie-tts.
# The container listens on 127.0.0.1:8881 only; reach it with  ssh -N -L 8881:localhost:8881 erebus
set -eu

HOST=${PIE_TTS_HOST:-erebus}
NAME=pie-tts
PORT=8881
DIR='~/pie-tts'
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
REV=$(git -C "$ROOT" rev-parse --short HEAD 2>/dev/null || echo dev)

remote() { ssh -o BatchMode=yes "$HOST" "$@"; }

run_container() {
  remote "docker run -d --name $NAME --restart unless-stopped \
    -p 127.0.0.1:$PORT:$PORT --cpus 6 --memory 6g --memory-swap 6g --pids-limit 256 \
    --read-only --tmpfs /tmp:size=256m --security-opt no-new-privileges --cap-drop ALL \
    --log-opt max-size=10m --log-opt max-file=3 \
    $NAME:latest"
}

case "${1:-deploy}" in
deploy)
  # Stage exactly the files the image needs, from the committed HEAD (not the working tree), so the image
  # tag pie-tts:<rev> names what it contains.
  STAGE=$(mktemp -d)
  trap 'rm -rf "$STAGE"' EXIT
  git -C "$ROOT" archive HEAD tts/erebus/Dockerfile tts/erebus/requirements.txt tts/erebus/server.py \
    pie/__init__.py pie/translit.py pie/phon.py pie/meter.py pie/ipa.py pie/speak.py \
    tts/espeak/mapping.json tts/kokoro/vocab.json | tar -C "$STAGE" -xf -
  mv "$STAGE"/tts/erebus/* "$STAGE/" && rmdir "$STAGE/tts/erebus"
  if ! git -C "$ROOT" diff --quiet HEAD -- tts/erebus pie/__init__.py pie/translit.py pie/phon.py pie/meter.py \
      pie/ipa.py pie/speak.py tts/espeak/mapping.json tts/kokoro/vocab.json; then
    echo "note: uncommitted changes to staged files are NOT deployed (building HEAD $REV)" >&2
  fi
  echo "$REV" > "$STAGE/REVISION"
  remote "rm -rf $DIR && mkdir -p $DIR"
  tar -C "$STAGE" -cf - . | remote "tar -C $DIR -xf -"
  remote "cd $DIR && docker build -t $NAME:$REV -t $NAME:latest ."
  remote "docker rm -f $NAME >/dev/null 2>&1 || true"
  run_container
  echo "waiting for /health ..."
  for _ in $(seq 1 60); do
    if remote "curl -sf http://127.0.0.1:$PORT/health" 2>/dev/null; then echo; exit 0; fi
    sleep 3
  done
  echo "not healthy after 180 s; see: sh tts/erebus/deploy.sh logs" >&2; exit 1 ;;
start)   remote "docker start $NAME" ;;
stop)    remote "docker stop $NAME" ;;
restart) remote "docker restart $NAME" ;;
status)  remote "docker ps -a --filter name=^/$NAME\$ --format '{{.Names}} {{.Image}} {{.Status}} {{.Ports}}'; \
                 docker stats --no-stream $NAME; curl -sf http://127.0.0.1:$PORT/health; echo" ;;
logs)    remote "docker logs --tail ${2:-100} $NAME" ;;
remove)  remote "docker rm -f $NAME; docker images -q $NAME | sort -u | xargs -r docker rmi -f; rm -rf $DIR" ;;
*) echo "usage: $0 [deploy|start|stop|restart|status|logs [N]|remove]" >&2; exit 2 ;;
esac
