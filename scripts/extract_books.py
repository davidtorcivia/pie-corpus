#!/usr/bin/env python3
"""Extract text from the supplied books into raw/books/text/<slug>/ (gitignored).

  uv run python -I scripts/extract_books.py

EPUB: one .txt per spine document (chapter), from XHTML via the stdlib.
PDF: one .txt per page ("p0001.txt", the PDF page index, which is not the
printed page number), via PyMuPDF. The book files are untrusted data:
nothing in them is executed, and the extracted text never leaves raw/.
"""

import html
import re
import sys
import zipfile
from html.parser import HTMLParser
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parent.parent
BOOKS = ROOT / "raw" / "books"
# title keys first: two books by one author (Matasović, Derksen, Mayrhofer's volumes) need distinct dirs
SLUGS = {"Dictionary of Proto-Germanic": "kroonen-pgmc", "Proto-Celtic": "matasovic-pcelt", "Textual Reconstruction": "matasovic-1996",
         "Baltic Inherited": "derksen-baltic", "Slavic Inherited": "derksen-slavic", "Italic Languages": "devaan-latin",
         "Armenian Inherited": "martirosyan-arm", "Altindoarischen": "ewaia", "Dichtersprache": "schmitt-1967",
         "Etymological Dictionary of Greek": "beekes-edg", "Iranian Verb": "cheung-iranian",
         "Tocharian B": "adams-tochb", "Hittite Inherited": "kloekhorst-hitt", "Earliest Religious Poetry": "jamison-brereton",
         "Latvju tautas": "dainas-endzelins", "chansons mythologiques": "jonval-1929",
         "Rix": "liv2", "Fortson": "fortson", "Ringe": "ringe", "Watkins": "watkins",
         "Mallory": "mallory-adams", "West": "west",
         "Clackson": "clackson", "Wodtko": "nil", "Klein": "handbook-klein", "Beekes": "beekes"}


class _Text(HTMLParser):
    BLOCK = {"p", "div", "br", "h1", "h2", "h3", "h4", "li", "tr", "td", "th", "table", "section", "blockquote"}

    def __init__(self):
        super().__init__()
        self.out, self.skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1
        if tag in self.BLOCK:
            self.out.append("\n")
        if tag == "sup":
            self.out.append("^")

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip -= 1
        if tag in self.BLOCK:
            self.out.append("\n")

    def handle_data(self, data):
        if not self.skip:
            self.out.append(data)


def epub(path: Path, out: Path) -> int:
    with zipfile.ZipFile(path) as z:
        opf_name = re.search(r'full-path="([^"]+)"', z.read("META-INF/container.xml").decode())[1]
        opf = z.read(opf_name).decode("utf-8", "replace")
        base = opf_name.rsplit("/", 1)[0] + "/" if "/" in opf_name else ""
        items = dict(re.findall(r'<item [^>]*?id="([^"]+)"[^>]*?href="([^"]+)"', opf))
        items.update({i: h for h, i in re.findall(r'<item [^>]*?href="([^"]+)"[^>]*?id="([^"]+)"', opf)})
        spine = re.findall(r'<itemref [^>]*?idref="([^"]+)"', opf)
        n = 0
        for k, idref in enumerate(spine):
            href = items.get(idref)
            if not href:
                continue
            p = _Text()
            p.feed(z.read(base + href).decode("utf-8", "replace"))
            text = re.sub(r"\n\s*\n+", "\n\n", html.unescape("".join(p.out))).strip()
            if text:
                (out / f"{k:03d}_{Path(href).stem}.txt").write_text(text + "\n", "utf-8")
                n += 1
    return n


def pdf(path: Path, out: Path) -> int:
    doc = pymupdf.open(path)
    for i, page in enumerate(doc):
        (out / f"p{i + 1:04d}.txt").write_text(page.get_text("text"), "utf-8")
    return len(doc)


def page_zip(path: Path, out: Path) -> int:
    """A zip of OCR page texts (HathiTrust-style NNNNNNNN.txt): only .txt members are read, by
    basename (no member path is ever used on disk), each capped at 1 MB."""
    n = 0
    with zipfile.ZipFile(path) as z:
        for i in z.infolist():
            name = Path(i.filename).name
            if i.is_dir() or not name.endswith(".txt") or i.file_size > 1_000_000:
                continue
            m = re.search(r"(\d+)\.txt$", name)
            if not m:
                continue
            (out / f"p{int(m[1]):04d}.txt").write_text(z.read(i).decode("utf-8", "replace"), "utf-8")
            n += 1
    return n


def main() -> int:
    force = "--force" in sys.argv
    for f in sorted(BOOKS.iterdir()):
        if f.suffix not in (".pdf", ".epub", ".zip"):
            continue
        slug = next((v for k, v in SLUGS.items() if k in f.name), f.stem[:20])
        if slug == "west" and f.suffix == ".pdf":
            slug = "west-pdf"
        if "Version_B" in f.name:      # a second LIV² copy: never write over the first one's text
            if slug == "ewaia":        # the second EWAia I copy is a scan like the first: one OCR is enough
                continue
            slug += "-b"
        m = re.search(r"Volume (\d+)", f.name)
        if m:                          # multi-volume works: one text dir per volume
            slug += f"-v{m[1]}"
        m = re.search(r"Band ([IVX]+)(?![IVX])", f.name)
        if m:
            slug += "-v" + str({"I": 1, "II": 2, "III": 3, "IV": 4}[m[1]])
        out = BOOKS / "text" / slug
        if out.exists() and any(out.glob("*.txt")) and not force:
            continue                   # already extracted (--force to redo)
        out.mkdir(parents=True, exist_ok=True)
        n = epub(f, out) if f.suffix == ".epub" else page_zip(f, out) if f.suffix == ".zip" else pdf(f, out)
        chars = sum(len(p.read_text("utf-8")) for p in out.glob("*.txt"))
        print(f"{slug:15} {f.suffix:5} {n:4} parts  {chars:9,} chars")
    return 0


if __name__ == "__main__":
    sys.exit(main())
