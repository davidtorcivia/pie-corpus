# LIV² transcription brief (raw/books/extract/liv2/)

You transcribe root entries from page images of Rix et al., *Lexikon der indogermanischen Verben* (2nd ed. 2001), for a research lexicon of Proto-Indo-European. The book is copyrighted: transcribe the structured fields below only; never copy footnotes or commentary.

**Pages:** `/Users/david/AI/PIE/raw/books/images/liv2-djvu/dNNNN.png` (NNNN = DjVu page index). View each with the Read tool.

**Ownership:** you own every entry whose HEADWORD (the bold root line, e.g. `*bʰeh₃g-  'braten, rösten'  IEW 113`) appears on one of your pages. If your last owned entry continues onto the next page, read that one extra page to finish it. Skip entries whose headword is on a page before your range: the previous agent owns them.

**For each entry, transcribe:**
- `headword_printed`: exactly as printed, with any homograph number (e.g. `1.*bʰeh₂-`). Use Unicode as printed: superscript h → ʰ, superscript w → ʷ, subscript digits → ₁ ₂ ₃, non-syllabic i/u with an arc below → i̯ u̯ (U+032F), syllabic resonants with a ring below → r̥ l̥ m̥ n̥, palatals as printed (k̑, ĝ, ḱ, ǵ…), acute and macron as printed, and a leading ? if printed.
- `meaning_de`: the German gloss in quotes, verbatim.
- `meaning_en`: your short English translation of that gloss.
- `iew`: e.g. "IEW 113" or "IEW 116-7" as printed, or null.
- `stems`: the main block's rows, each `{"label": "Präsens" | "Aorist" | "Perfekt" | "Kausativ" | "Iterativ" | "Desider." | "Fientiv" | "Essiv" | … as printed, "form_printed": "the PIE stem as printed, e.g. *bʰéh₃g-/bʰh₃g-", "uncertain": true if it starts with ?}`. A label with several stems gives several rows with the same label.
- `neubildungen`: the labels listed after "Neubildungen:" (e.g. ["s-Aorist", "redupl. Aor."]). These are post-PIE formations: labels only, no forms.
- `uncertain_chars`: true if any character of the headword or a stem was hard to read.
- `djvu_page` (the file's page index) and `printed_page` (the number printed at the top of the page, if visible).

Do NOT transcribe the daughter-language reflex column, the footnotes, or the bibliography.

**Output:** APPEND to `/Users/david/AI/PIE/raw/books/extract/liv2/chunk-<NN>.jsonl`, one entry per line, after finishing each page and before opening the next. After each page also append `{"_page_done": NNNN}`. If you run low on room, stop cleanly after a page.

Never invent an entry or a form. If a page is unreadable, append `{"_page_unreadable": NNNN}` and move on.

Final message ≤100 words: pages done, entries written, and any unreadable pages.
