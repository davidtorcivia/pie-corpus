"""OCR scanned book PDFs into raw/books/text/<slug>/p####.txt with the macOS Vision tool (ocr).
usage: python -I vision_ocr.py <pdf> <outdir> <ocr-binary>   (pages already done are skipped)"""
import subprocess, sys, pathlib, tempfile, pymupdf
pdf, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
# build the Vision tool first: swiftc -O scripts/ocr/vision_ocr.swift -o <scratch>/ocr; pass its path as argv[3]
tool = pathlib.Path(sys.argv[3])
png = pathlib.Path(tempfile.gettempdir()) / f"page-{out.name}.png"
d = pymupdf.open(pdf)
for i, page in enumerate(d):
    t = out / f"p{i + 1:04d}.txt"
    if t.exists():
        continue
    page.get_pixmap(dpi=300).save(png)
    r = subprocess.run([str(tool), str(png), "de-DE,en-US,el-GR"], capture_output=True, text=True)
    t.write_text(r.stdout, "utf-8")
print(out.name, len(d))
