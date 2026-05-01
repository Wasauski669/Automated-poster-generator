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

def load_quotes_es():
    with open(COUNTER_FILE, "r", newline="") as counter_file:
        counter_reader = csv.DictReader(counter_file)
        counter_rows = list(counter_reader)

    last_counter_row = counter_rows[-1]

    c_quote = int(last_counter_row["counter_quote"])
    c_quote_es = int(last_counter_row["counter_quote_es"])
    c_background = int(last_counter_row["counter_background"])

    print("c_quote_es:", c_quote_es)

    with open(QUOTES_FILE, "r", newline="") as quotes_file:
        quotes_reader = csv.DictReader(quotes_file)
        quote_rows = list(quotes_reader)

    quote_index = c_quote_es % len(quote_rows)

    selected_quote_es_row = quote_rows[quote_index]

    reference_es = selected_quote_es_row["References_es"]
    quote_es = selected_quote_es_row["Quotes_es"]

    print("reference:", reference_es)
    print("quote:", quote_es)

    with open(COUNTER_FILE, "a", newline="") as counter_file:
        fieldnames = ["counter_quote", "counter_background", "counter_quote_es"]
        writer = csv.DictWriter(counter_file, fieldnames=fieldnames)

        writer.writerow({
            "counter_quote": c_quote,
            "counter_background": c_background,
            "counter_quote_es": c_quote_es + 1
        })

    return reference_es, quote_es

load_quotes_es()