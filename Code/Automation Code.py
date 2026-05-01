import subprocess
from PIL import Image
from jinja2 import Environment, FileSystemLoader
import csv
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

TEMPLATE_DIR = BASE_DIR/"Latex-Poster"
OUTPUT_DIR = BASE_DIR/"output"
PHOTOS_DIR = BASE_DIR/"Assets"/"Fotos"
QUOTES_FILE = BASE_DIR/"Assets"/"Quotes"/"quotes_with_spanish.csv"
COUNTER_FILE = BASE_DIR/"Code"/"counter.csv"

OUTPUT_DIR.mkdir(exist_ok=True)

def latex_escape(text: str) -> str:
    """
    Prevents special LaTeX characters from breaking your document.
    """
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text

def latex_path(path: Path) -> str:
    """
    Converts a Python path into something LaTeX can read.
    """
    return "{" + path.as_posix() + "}"


def load_quotes_en():
    with open(COUNTER_FILE, "r", newline="") as counter_file:
        counter_reader = csv.DictReader(counter_file)
        counter_rows = list(counter_reader)

    last_counter_row = counter_rows[-1]

    c_quote = int(last_counter_row["counter_quote"])
    print("c_quote:", c_quote)

    with open(QUOTES_FILE, "r", newline="") as quotes_file:
        quotes_reader = csv.DictReader(quotes_file)
        quote_rows = list(quotes_reader)

    c_quote = c_quote % len(quote_rows)

    selected_quote_row = quote_rows[c_quote]

    cell1 = selected_quote_row["Reference"]
    cell2 = selected_quote_row["Quote"]
    print("cell1:", cell1)
    print("cell2:", cell2)


    with open(COUNTER_FILE, "a", newline="")as counter_file:
        fieldnames = ["counter_quote"]
        writer = csv.DictWriter(counter_file, fieldnames=fieldnames)

        writer.writerow({"counter_quote": (c_quote+1)})





def load_quotes_es():
    #LOAD QUOTES IN SPANISH
    pass

def load_backgrounds():
    #LOAD BACKGROUNDS GOES HERE"
    pass


def compile_tex(tex_file: Path):
    subprocess.run(
        [
            "xelatex",
            "-interaction=nonstopmode",
            "-output-directory",
            str(OUTPUT_DIR),
            str(tex_file),
        ],
        check=True,
    )

def main():
    pass

if __name__ == "__main__":
    main()