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
        #"\\": r"\textbackslash{}",
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
    return path.as_posix()


def load_quotes_en():
    #READS THE COUNTER CSV FILE
    with open(COUNTER_FILE, "r", newline="") as counter_file:
        counter_reader = csv.DictReader(counter_file)
        counter_rows = list(counter_reader)

    last_counter_row = counter_rows[-1]

    c_quote = int(last_counter_row["counter_quote"])
    c_quote_es = int(last_counter_row["counter_quote_es"])
    c_background = int(last_counter_row["counter_background"])

    print("c_quote_es:", c_quote_es)
    print("c_quote: ", c_quote)
    print("c_background: ", c_background)

    #READS THE QUOTES CSV FILE
    with open(QUOTES_FILE, "r", newline="") as quotes_file:
        quotes_reader = csv.DictReader(quotes_file)
        quote_rows = list(quotes_reader)

    quote_index = c_quote_es % len(quote_rows)

    selected_quote_es_row = quote_rows[quote_index]

    #SELECTS THE COLUMN ON THE CSV FILE
    reference_en = selected_quote_es_row["Reference"]
    quote_en = selected_quote_es_row["Quote"]

    print("reference:", reference_en)
    print("quote:", quote_en)

    #WRITES THE CSV COUNTER FILE 
    with open(COUNTER_FILE, "a", newline="") as counter_file:
        fieldnames = ["counter_quote", "counter_background", "counter_quote_es"]
        writer = csv.DictWriter(counter_file, fieldnames=fieldnames)

        writer.writerow({
            "counter_quote": c_quote + 1,
            "counter_background": c_background,
            "counter_quote_es": c_quote_es
        })

    return reference_en, quote_en


def load_quotes_es():
    #READS THE COUNTER CSV FILE
    with open(COUNTER_FILE, "r", newline="") as counter_file:
        counter_reader = csv.DictReader(counter_file)
        counter_rows = list(counter_reader)

    last_counter_row = counter_rows[-1]

    c_quote = int(last_counter_row["counter_quote"])
    c_quote_es = int(last_counter_row["counter_quote_es"])
    c_background = int(last_counter_row["counter_background"])

    print("c_quote_es:", c_quote_es)
    print("c_quote: ", c_quote)
    print("c_background: ", c_background)

    #READS THE QUOTES CSV FILE
    with open(QUOTES_FILE, "r", newline="") as quotes_file:
        quotes_reader = csv.DictReader(quotes_file)
        quote_rows = list(quotes_reader)

    quote_index = c_quote_es % len(quote_rows)

    selected_quote_es_row = quote_rows[quote_index]

    reference_es = selected_quote_es_row["References_es"]
    quote_es = selected_quote_es_row["Quotes_es"]

    print("reference:", reference_es)
    print("quote:", quote_es)

    #WRITES THE CSV COUNTER FILE 
    with open(COUNTER_FILE, "a", newline="") as counter_file:
        fieldnames = ["counter_quote", "counter_background", "counter_quote_es"]
        writer = csv.DictWriter(counter_file, fieldnames=fieldnames)

        writer.writerow({
            "counter_quote": c_quote,
            "counter_background": c_background,
            "counter_quote_es": c_quote_es + 1
        })

    return reference_es, quote_es

def load_background():
    with open(COUNTER_FILE, "r", newline="") as counter_file:
        counter_reader = csv.DictReader(counter_file)
        counter_rows = list(counter_reader)

    last_counter_row = counter_rows[-1]

    c_quote = int(last_counter_row["counter_quote"])
    c_quote_es = int(last_counter_row["counter_quote_es"])
    c_background = int(last_counter_row["counter_background"])
    select_foto = PHOTOS_DIR/f"backgroundfoto{c_background}.jpg"
    print("Bg Foto: ", select_foto)

    if not select_foto.exists():
        print("File does not exist: ", select_foto)
        return None
    
    with open(COUNTER_FILE, "a", newline="") as counter_file:
        fieldnames = ["counter_quote", "counter_background", "counter_quote_es"]
        writer = csv.DictWriter(counter_file, fieldnames=fieldnames)

        writer.writerow({
            "counter_quote": c_quote,
            "counter_background": c_background + 1,
            "counter_quote_es": c_quote_es
            })
    
    return select_foto


def compile_tex(tex_file: Path):
    subprocess.run(
        [
            "xelatex",
            "-interaction=nonstopmode",
            tex_file.name,
        ],
        cwd=tex_file.parent,
        check=True,
    )

def main():
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=False)

    template = env.get_template("Latexcode.tex")
    references_es, quotes_es = load_quotes_es()
    background = load_background()
    print(references_es,quotes_es)

    if not quotes_es:
        raise RuntimeError("No quotes found in Assets/Quotes")
    
    if not background:
        raise RuntimeError("No background Images")
    
    render_tex = template.render(bgimage = latex_path(background),
                                 Quote = quotes_es,
                                 Reference = references_es)
    
    tex_file = OUTPUT_DIR /"Poster-output.tex"
    tex_file.write_text(render_tex, encoding="utf-8")
    print(render_tex[:1000])
    compile_tex(tex_file)
    print("generated poster successfully.")

if __name__ == "__main__":
    main()