"""OCR a scanned PDF with Tesseract, pages in parallel.
usage: python -I tess_ocr.py <pdf> <outdir> <langs> [workers]   (done pages are skipped)"""
import subprocess, sys, pathlib, tempfile, concurrent.futures as cf, pymupdf
pdf, out, langs = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), sys.argv[3]
workers = int(sys.argv[4]) if len(sys.argv) > 4 else 6
out.mkdir(parents=True, exist_ok=True)
tmp = pathlib.Path(tempfile.mkdtemp(prefix="tess-"))
n = len(pymupdf.open(pdf))

def one(i):
    t = out / f"p{i + 1:04d}.txt"
    if t.exists():
        return
    png = tmp / f"{i}.png"
    pymupdf.open(pdf)[i].get_pixmap(dpi=400).save(png)
    r = subprocess.run(["tesseract", str(png), "-", "-l", langs], capture_output=True, text=True)
    t.write_text(r.stdout, "utf-8")
    png.unlink()

with cf.ThreadPoolExecutor(workers) as ex:
    list(ex.map(one, range(n)))
print(out.name, n)
