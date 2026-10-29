#!/bin/sh
# Compile the PIE eSpeak-NG voice into a private data dir: tts/espeak/build/data (gitignored).
# The system install (Homebrew) is only read, never changed. Needs: brew install espeak-ng (1.52.0), git, network
# for the one-time source clone (the phoneme sources are not shipped by Homebrew).
#   sh tts/espeak/build.sh            # build (re-uses the clone if present)
#   sh tts/espeak/build.sh --clean    # delete build/ first
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
B="$HERE/build"
TAG=1.52.0
COMMIT=4870adfa25b1a32b4361592f1be8a40337c58d6c     # espeak-ng tag 1.52.0
[ "${1:-}" = "--clean" ] && rm -rf "$B"

command -v espeak-ng >/dev/null || { echo "espeak-ng not found: brew install espeak-ng" >&2; exit 1; }
HAVE=$(espeak-ng --version | sed -n 's/.*speech: \([0-9.]*\).*/\1/p')
[ "$HAVE" = "$TAG" ] || { echo "espeak-ng $HAVE installed; this table is built and tested for $TAG" >&2; exit 1; }
SYS=$(espeak-ng --version | sed -n 's/.*Data at: //p')
[ -d "$SYS/voices" ] || { echo "cannot find the installed espeak-ng-data (got '$SYS')" >&2; exit 1; }

mkdir -p "$B"
if [ ! -d "$B/src/phsource" ]; then
  rm -rf "$B/src"
  git -c advice.detachedHead=false clone -q --depth 1 --branch "$TAG" https://github.com/espeak-ng/espeak-ng.git "$B/src"
fi
GOT=$(git -C "$B/src" rev-parse HEAD)
[ "$GOT" = "$COMMIT" ] || { echo "espeak-ng source at $GOT, expected $COMMIT ($TAG)" >&2; exit 1; }

rm -rf "$B/data" && mkdir -p "$B/data"
cp -R "$SYS" "$B/data/espeak-ng-data" && chmod -R u+w "$B/data/espeak-ng-data"
cp -R "$B/src/phsource" "$B/data/phsource"
cp "$HERE/ph_pie" "$B/data/phsource/ph_pie"
printf '\nphonemetable pie hi\ninclude ph_pie\n' >> "$B/data/phsource/phonemes"
mkdir -p "$B/data/espeak-ng-data/voices/pie"
cp "$HERE/voices/pie/pie" "$HERE/voices/pie/pie-tone" "$B/data/espeak-ng-data/voices/pie/"

LOG=$(ESPEAK_DATA_PATH="$B/data" espeak-ng --compile-phonemes="$B/data/phsource" 2>&1) || true
echo "$LOG" | tail -n 3
echo "$LOG" | grep -q " 0 errors" || { echo "phoneme compile reported errors (see $B/data/phsource/compile_report)" >&2; exit 1; }
OUT=$(ESPEAK_DATA_PATH="$B/data" espeak-ng -v pie/pie -q --ipa "[[H'ekwos ?esti:]]")
echo "smoke: [[H'ekwos ?esti:]] -> $OUT"
[ "$OUT" = "ħˈekwos ʔestiː" ] || { echo "smoke test failed" >&2; exit 1; }
echo "built: ESPEAK_DATA_PATH=$B/data"
