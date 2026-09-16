#!/usr/bin/env python3
"""Converte declaracao_uso_ia.md em PDF via HTML + Chromium headless (Edge ou Chrome)."""
import shutil
import subprocess
import tempfile
from pathlib import Path

import markdown

SRC = Path("declaracao_uso_ia.md")
HTML_OUT = Path("declaracao_uso_ia.html")
PDF_OUT = Path("declaracao_uso_ia.pdf")

CSS = """
<style>
body { font-family: 'Segoe UI', Arial, sans-serif; max-width: 900px; margin: 40px auto; line-height: 1.5; color: #1a1a1a; }
h1, h2, h3 { color: #0b3d91; }
h1 { font-size: 1.6em; border-bottom: 2px solid #0b3d91; padding-bottom: 6px; }
h2 { font-size: 1.3em; margin-top: 1.6em; border-bottom: 1px solid #ccc; padding-bottom: 4px; }
table { border-collapse: collapse; width: 100%; margin: 1em 0; font-size: 0.85em; }
th, td { border: 1px solid #999; padding: 6px 8px; text-align: left; }
th { background: #eef2fb; }
code { background: #f2f2f2; padding: 1px 5px; border-radius: 3px; font-size: 0.9em; }
pre { background: #f2f2f2; padding: 10px; overflow-x: auto; }
blockquote { border-left: 4px solid #0b3d91; margin: 1em 0; padding: 0.2em 1em; background: #f7f9fd; }
a { color: #0b3d91; }
</style>
"""


def convert_md_to_html():
    text = SRC.read_text(encoding="utf-8")
    body = markdown.markdown(text, extensions=["tables", "fenced_code"])
    title = "Declaracao de Uso de IA Generativa - SO Atividade 1 - Leticia Cavalcanti"
    html = f"<!doctype html><html><head><meta charset='utf-8'><title>{title}</title>{CSS}</head><body>{body}</body></html>"
    HTML_OUT.write_text(html, encoding="utf-8")
    print(f"HTML gerado: {HTML_OUT}")


def find_browser():
    candidates = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    ]
    for c in candidates:
        if Path(c).exists():
            return c
    return shutil.which("msedge") or shutil.which("chrome")


def convert_html_to_pdf():
    browser = find_browser()
    if not browser:
        print("Nenhum navegador Chromium encontrado para gerar o PDF automaticamente.")
        print(f"Abra {HTML_OUT} no navegador e use Imprimir > Salvar como PDF.")
        return
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
    convert_md_to_html()
    convert_html_to_pdf()
