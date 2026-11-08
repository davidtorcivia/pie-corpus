#!/bin/bash
# errs.sh DIR: each run's first error line and exit
for d in "$1"/*/; do echo "== $(basename $d)"; grep -E "OutOfMemoryError|CheckpointError|Error:|EXIT" "$d/console.log" | head -3 | cut -c1-200; done
