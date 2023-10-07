import csv
import pickle
import re
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from pathlib import Path
from typing import List, Tuple, Pattern, AnyStr

import numpy as np
from tqdm import tqdm

from cell import crop_cells, process_cell, get_cell_main
from pdf import read_pdf

DATA_DIR = 'data'
OUTPUT_DIR = 'output'

HEADER = ["SL No", "Reg No", "Name", "Relation", "Father / Husband / Mother", "Address", "Age", "Gender", "LAC No",
          "LAC name", "Booth No", "Booth Name"]


def replace(*texts, replacements: List[Tuple[Pattern[AnyStr], str]]):
    ret = []

    for text in texts:
        for pattern, replacement in replacements:
            text = re.sub(pattern, replacement, text)
        ret.append(text)

    return ret


def clean(details, prefix_lookup, replacements: List[Tuple[Pattern[AnyStr], str]]):
    if len(details) != 8:
        return details + [""] * (8 - len(details))

    sl_no, voter_id, name, relation, husband, house, age, gender = details

    voter_id = re.sub(r'[^a-z0-9]+', '', voter_id.lower())
    prefix, number = voter_id[:3], voter_id[-7:].replace("o", "0")

    voter_id = prefix_lookup[prefix] + number if len(prefix) == 3 else ''

    age_match = re.search(r'\d{2}|\d\s+\d', age)
    age = age_match.group().replace(" ", "") if age_match else ''

    symbols = re.compile(r"[₹!@#$%^&*()1-9]")

    name, husband = symbols.sub('', name), symbols.sub('', husband)
    name, husband, house = replace(name, husband, house, replacements=replacements)

    return [sl_no, voter_id.upper(), name, relation, husband, house, age, gender]


def get_lac_booth(path: Path):
    name = path.stem.upper()
    lac, booth = name.split("A")[-1].split("P")
    lac_booth = np.load("res/lac_booth.npy", allow_pickle=True)

    return [lac, lac_booth[int(lac)][0], booth, lac_booth[int(lac)][int(booth)]]


def process_pdf(path, prefix_lookup, replacements):
    rows_for_pdf = []
    empty_for_pdf = []
    cover = get_lac_booth(path)

    pages = read_pdf(str(path))
    _ = next(pages), next(pages)

    sl_no = 0

    for page in pages:
        for cell in crop_cells(page):
            sl_no += 1
            cell, voter_id = process_cell(cell)

            details = get_cell_main(cell)

            if not details:
                empty_for_pdf.append([sl_no, voter_id, *([""] * 6), *cover])

            details.insert(0, str(sl_no))
            details.insert(1, voter_id)

            details = clean(details, prefix_lookup, replacements)
            rows_for_pdf.append(details + cover)

    print(f"Processed {path.stem} with {sl_no} entries")

    return rows_for_pdf, empty_for_pdf


def main():
    Path(OUTPUT_DIR).mkdir(exist_ok=True)
    prefix_lookup = pickle.load(open('res/prefix_lookup.pkl', 'rb'))
    replacements = []

    with open('res/replacements.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            replacements.append((re.compile(row[0]), row[1].replace("/s", " ")))

    rows = [HEADER]
    empty = [HEADER]

    processor = partial(process_pdf, prefix_lookup=prefix_lookup, replacements=replacements)

    paths = list(Path(DATA_DIR).glob('**/*.pdf'))

    with ProcessPoolExecutor() as executor:
        results = executor.map(processor, paths)

    for rows_for_pdf, empty_for_pdf in list(results):
        rows.extend(rows_for_pdf)
        empty.extend(empty_for_pdf)

    # Write to CSV
    with open(f'{OUTPUT_DIR}/output.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    with open(f'{OUTPUT_DIR}/empty.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(empty)


if __name__ == '__main__':
    main()
