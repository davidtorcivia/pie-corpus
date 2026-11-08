#!/bin/bash
# grep helper: g.sh PATTERN FILE [N]
grep -E "$1" "$2" | head -${3:-20} | cut -c1-${4:-400}
