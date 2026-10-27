# -*- coding: utf-8 -*-
import os
import sys
import argparse
import subprocess
import csv
import shutil
import re

def find_par_files(root):
    par_files = []
    for dirpath, dirnames, filenames in os.walk(root):
        # Only consider directories named "e"
        if os.path.basename(dirpath) == "e":
            for f in filenames:
                if f.lower().endswith(".par"):
                    par_files.append(os.path.join(dirpath, f))
    return par_files

def extract_par(par_path, tmp_dir):
    cmd = ["C:/mODS/yakuza6/herramientas/partool/ParTool.exe", "extract", "-r", par_path, tmp_dir]
    result = subprocess.run(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
    if result.returncode != 0:
        raise RuntimeError(f"ParTool failed for {par_path}: {result.stderr.decode('utf-8', errors='ignore')}"
)

def es_cjk(c):
    o = ord(c)
    return 0x2E80 <= o <= 0x9FFF or 0xAC00 <= o <= 0xD7AF or 0xF900 <= o <= 0xFAFF or 0xFF00 <= o <= 0xFFEF


def read_cmn_bin(bin_path):
    # Campos de texto alineados a 4 bytes y rellenos de ceros; tras cada campo inglés va su versión china,
    # así que el sitio disponible es la distancia hasta el siguiente byte no nulo.
    data = open(bin_path, "rb").read()
    strings = []
    n = len(data)
    for start in range(4, n, 4):
        if data[start] == 0 or data[start - 1] != 0:
            continue
        end = data.find(bytes(1), start)
        if end < 0 or end - start < 4:
            continue
        chunk = data[start:end]
        try:
            text = chunk.decode("utf-8")
        except UnicodeDecodeError:
            continue
        if not text.isprintable() or any(es_cjk(c) for c in text):
            continue
        if not text.isascii() and sum(c.isascii() for c in text) < len(text) * 0.8:
            continue
        if not re.search(r"[A-Za-z]{2,}", text):
            continue
        sin_esp = text.replace(" ", "")
        if sum(c.isalpha() for c in sin_esp) < len(sin_esp) * 0.6:
            continue
        if " " in text:
            if sum(c.isalpha() for c in text) < 3:
                continue
        else:
            # una sola palabra: nombres de personaje o etiquetas; nada de nombres internos ni basura binaria
            if "_" in text or len(text) < 5 or not re.fullmatch(r"[A-Z][a-z]+(-[a-z]+)?[.!?]*", text):
                continue
        fin = end
        while fin < n and data[fin] == 0:
            fin += 1
        hueco = ((fin - start) // 4) * 4 - 1
        # tras la última frase de un bloque puede haber ceros que no son relleno: no pasar de 63 salvo que el original ya lo haga
        hueco = min(hueco, max(63, ((len(chunk) + 16) // 16) * 16 - 1))
        if hueco < len(chunk):
            hueco = len(chunk)
        strings.append((start, hueco, text))
    return strings

def main():
    parser = argparse.ArgumentParser(description="Extract English text from Yakuza 6 .par files")
    parser.add_argument("--limite", type=int, default=None, help="limit number of files to process")
    args = parser.parse_args()

    root = r"C:/mODS/yakuza6/trabajo/extraido/talk"
    out_csv = r"C:/mODS/yakuza6/trabajo/talk_ingles.csv"
    tmp_root = r"C:/mODS/yakuza6/trabajo/tmp"
    os.makedirs(tmp_root, exist_ok=True)

    par_files = find_par_files(root)
    if args.limite:
        par_files = par_files[:args.limite]
    total_files = len(par_files)

    rows = []
    for par_path in par_files:
        # extract to unique subfolder
        rel = os.path.relpath(par_path, root)
        subfolder = os.path.join(tmp_root, os.path.splitext(rel)[0])
        shutil.rmtree(subfolder, ignore_errors=True)
        try:
            extract_par(par_path, subfolder)
        except Exception as e:
            print(f"Error extracting {par_path}: {e}", file=sys.stderr)
            continue
        cmn_bin = os.path.join(subfolder, "cmn.par", "cmn.bin")
        if not os.path.exists(cmn_bin):
            print(f"cmn.bin missing for {par_path}", file=sys.stderr)
            continue
        strings = read_cmn_bin(cmn_bin)
        for offset, bmax, txt in strings:
            rows.append((par_path, str(offset), str(bmax), str(len(txt.encode("utf-8"))), txt, ""))

    # write csv
    with open(out_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["archivo_par", "offset", "bytes_max", "bytes_ingles", "ingles", "espanol"])
        writer.writerows(rows)

    print(f"Procesados {total_files} archivos, {len(rows)} filas")

if __name__ == "__main__":
    main()
