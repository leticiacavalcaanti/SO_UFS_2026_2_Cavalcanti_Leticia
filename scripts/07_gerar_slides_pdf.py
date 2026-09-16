#!/usr/bin/env python3
"""Converte report/apresentacao.md (slides separados por '---') em PDF paisagem."""
import subprocess
import tempfile
from pathlib import Path

import markdown

SRC = Path("report/apresentacao.md")
HTML_OUT = Path("report/apresentacao.html")
PDF_OUT = Path("report/apresentacao.pdf")

CSS = """
<style>
@page { size: A4 landscape; margin: 18mm; }
body { font-family: 'Segoe UI', Arial, sans-serif; color: #1a1a1a; font-size: 20px; }
h1 { font-size: 2em; color: #0b3d91; }
h2 { font-size: 1.6em; color: #0b3d91; border-bottom: 2px solid #0b3d91; padding-bottom: 6px; }
table { border-collapse: collapse; width: 100%; margin: 0.6em 0; font-size: 0.75em; }
th, td { border: 1px solid #999; padding: 6px 10px; text-align: left; }
th { background: #eef2fb; }
code, pre { background: #f2f2f2; padding: 2px 6px; border-radius: 3px; font-size: 0.8em; }
pre { padding: 10px; }
hr { border: none; page-break-after: always; margin: 0; }
li { margin-bottom: 0.3em; }
img { max-width: 100%; max-height: 115mm; display: block; margin: 6px auto; }
p { margin: 0.4em 0; }
</style>
"""


def main():
    text = SRC.read_text(encoding="utf-8")
    body = markdown.markdown(text, extensions=["tables", "fenced_code"])
    title = "Apresentacao - SO Atividade 1 - Leticia Cavalcanti"
    html = f"<!doctype html><html><head><meta charset='utf-8'><title>{title}</title>{CSS}</head><body>{body}</body></html>"
    HTML_OUT.write_text(html, encoding="utf-8")
    print(f"HTML gerado: {HTML_OUT}")

    browser = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    if not Path(browser).exists():
        browser = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    html_abs = HTML_OUT.resolve()
    pdf_abs = PDF_OUT.resolve()
    with tempfile.TemporaryDirectory(prefix="edge-print-") as tmp_profile:
        cmd = [
            browser, "--headless=new", "--disable-gpu", "--no-sandbox",
            f"--user-data-dir={tmp_profile}",
            "--no-pdf-header-footer",
            f"--print-to-pdf={pdf_abs}", f"file:///{html_abs.as_posix()}",
        ]
        subprocess.run(cmd, check=True, timeout=60)
    print(f"PDF gerado: {PDF_OUT}")


if __name__ == "__main__":
    main()
