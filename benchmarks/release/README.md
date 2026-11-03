# Release page and images

`build.py` reads `../results/summary.json` and writes `index.html` (the published page, artifact
https://claude.ai/artifact/SHamuAuZSYZ6D91NPv1RY4) and `cards.html` (one 1600×900 card per figure). The PNGs in
`img/` are those cards rendered at 2× by headless Chrome:

    python3 build.py
    for n in leaderboard segments notation effort progress; do for t in light dark; do
      "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --hide-scrollbars \
        --allow-file-access-from-files --force-device-scale-factor=2 --window-size=1600,900 \
        --virtual-time-budget=4000 --screenshot=img/$n-$t.png "file://$PWD/cards.html#$n-$t"; done; done

Fonts (all SIL OFL, from github.com/google/fonts): Bricolage Grotesque, IBM Plex Sans and Mono, Gentium Book Plus.
