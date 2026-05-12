import subprocess
from PIL import Image
import numpy as np
from jinja2 import Environment, FileSystemLoader
import csv
from pathlib import Path
import time 


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


def load_background(update_counter=False):
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
    
    if update_counter:
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
    result = subprocess.run(
        [
            "xelatex",
            "-interaction=nonstopmode",
            "-halt-on-error",
            tex_file.name,
        ],
        cwd=tex_file.parent,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:
        print("LaTeX compilation failed:")
        print(result.stdout)
        print(result.stderr)
        raise RuntimeError("xelatex failed")


def detect_color():
    bg = load_background(update_counter=False)
    img = Image.open(bg).convert("RGB")
    width, height = img.size

    regions = {
        "Grupo de":        (0.15, 0.00, 0.85, 0.18),
        "Oracion":         (0.05, 0.10, 0.95, 0.38),
        "Viernes 19:30h":  (0.20, 0.31, 0.80, 0.45),
        "Quote":           (0.10, 0.78, 0.90, 0.95),
        "Reference":       (0.25, 0.89, 0.75, 1.00),
    }
    boxes = {
        "Grupo de": (regions["Grupo de"][0] * width, 
                     regions["Grupo de"][1] * height, 
                     regions["Grupo de"][2] * width, 
                     regions["Grupo de"][3] * height),
        "Oracion": (regions["Oracion"][0] * width,
                     regions["Oracion"][1] * height,
                     regions["Oracion"][2] * width,
                     regions["Oracion"][3] * height),
        "Viernes 19:30": (regions["Viernes 19:30h"][0] * width,
                          regions["Viernes 19:30h"][1] * height,
                          regions["Viernes 19:30h"][2] * width,
                          regions["Viernes 19:30h"][3] * height),
        "Quote": (regions["Quote"][0] * width,
                  regions["Quote"][1] * height,
                  regions["Quote"][2] * width,
                  regions["Quote"][3] * height),
        "Reference": (regions["Reference"][0] * width,
                      regions["Reference"][1] * height,
                      regions["Reference"][2] * width,
                      regions["Reference"][3] * height)
    }
    
    
    Grupo_de = boxes["Grupo de"]
    Oracion = boxes["Oracion"]
    Viernes = boxes["Viernes 19:30"]
    Quote = boxes["Quote"]
    Reference = boxes["Reference"]

    crop_grupo_de= img.crop(Grupo_de)
    crop_Oracion = img.crop(Oracion)
    crop_Viernes = img.crop(Viernes)
    crop_Quote = img.crop(Quote)
    crop_Reference = img.crop(Reference)

    arr1 = np.array(crop_grupo_de).astype(float)
    arr2 = np.array(crop_Oracion).astype(float)
    arr3 = np.array(crop_Viernes).astype(float)
    arr4 = np.array(crop_Quote).astype(float)
    arr5 = np.array(crop_Reference).astype(float)

    BRIGHTNESS = [(0.2126 * arr1[:,:,0]+ 0.7152 * arr1[:,:,1] + 0.0722 * arr1[:,:,2]),
                  (0.2126 * arr2[:,:,0]+ 0.7152 * arr2[:,:,1] + 0.0722 * arr2[:,:,2]),
                  (0.2126 * arr3[:,:,0]+ 0.7152 * arr3[:,:,1] + 0.0722 * arr3[:,:,2]),
                  (0.2126 * arr4[:,:,0]+ 0.7152 * arr4[:,:,1] + 0.0722 * arr4[:,:,2]),
                  (0.2126 * arr5[:,:,0]+ 0.7152 * arr5[:,:,1] + 0.0722 * arr5[:,:,2])
    ]
    avg_brightness = []
    for i in range(len(BRIGHTNESS)):
        avg_brightness.append(BRIGHTNESS[i].mean())

    print("COLOR BRIGHTNESS: ", avg_brightness)
    return avg_brightness


def chose_color():
    BRIGHTNESS = detect_color()

    colors = []
    shadows = []

    for i in range(len(BRIGHTNESS)):
        if BRIGHTNESS[i] < 120:
            colors.append("cream")
            shadows.append("shadowforcream")
        elif BRIGHTNESS[i] < 160:
            colors.append("black")
            shadows.append("shadowforblack")
        else:
            colors.append("darkbrown")
            shadows.append("shadowforbrown")
    
    return colors, shadows


def pdf_to_png(pdf_path, png_path):
    subprocess.run(
        [
            "convert",
            "-density","300",
            str(pdf_path),
            "-quality","100",
            str(png_path)
        ],
        check=True
    )


def main():
    start_time = time.time()
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=False)

    template = env.get_template("Latexcode.tex")
    references_es, quotes_es = load_quotes_es()
    letter_color = chose_color()
    background = load_background(update_counter=True)
    print(references_es,quotes_es)

    if not quotes_es:
        raise RuntimeError("No quotes found in Assets/Quotes")
    
    if not background:
        raise RuntimeError("No background Images")
    
    render_tex = template.render(bgimage = latex_path(background),
                                 Quote = quotes_es,
                                 Reference = references_es,
                                 Color = letter_color[0][0],
                                 Grupo_de = letter_color[0][0],
                                 Oracion = letter_color[0][1],
                                 Viernes = letter_color[0][2],
                                 QUOTE = letter_color[0][3],
                                 REFERENCE = letter_color[0][4],
                                 SColor = letter_color[1][0],
                                 SGrupo_de = letter_color[1][0],
                                 SOracion = letter_color[1][1],
                                 SViernes = letter_color[1][2],
                                 SQUOTE = letter_color[1][3],
                                 SREFERENCE = letter_color[1][4])
    
    tex_file = OUTPUT_DIR /"Poster-output.tex"
    tex_file.write_text(render_tex, encoding="utf-8")
    pdf_file = OUTPUT_DIR / "Poster-output.pdf"
    png_file = OUTPUT_DIR / "Poster-output.png"
    compile_tex(tex_file)
    pdf_to_png(pdf_file, png_file)
    print("COLOR: ", letter_color)
    print("generated poster successfully.")
    
    end_time = time.time()
    runtime = end_time - start_time
    print(f"Runtime: {runtime:.2f} seconds")


if __name__ == "__main__":
    main()