import csv
import pickle
import re
from pathlib import Path
from typing import List, Tuple, Pattern, AnyStr

from cell import crop_cells, process_cell, get_cell_main
from cover import process_cover
from pdf import read_pdf

DATA_DIR = 'data'
OUTPUT_DIR = 'output'


def clean(details, prefix_lookup, replacements: List[Tuple[Pattern[AnyStr], str]]):
    sl_no, voter_id, name, relation, husband, house, age, gender = details

    voter_id = re.sub(r'\W+', '', voter_id)
    prefix, number = voter_id[:3].lower(), voter_id[-7:].upper().replace("O", "0")

    voter_id = prefix_lookup[prefix] + number if len(prefix) == 3 else ''

    age_match = re.search(r'\d{2}|\d\s+\d', age)
    age = age_match.group().replace(" ", "") if age_match else ''

    name, husband = re.sub(r'\d+', '', name), re.sub(r'\d+', '', husband)

    for pattern, replacement in replacements:
        name = pattern.sub(replacement, name)
        husband = pattern.sub(replacement, husband)
        house = pattern.sub(replacement, house)

    return [sl_no, voter_id, name, relation, husband, house, age, gender]


def main():
    Path(OUTPUT_DIR).mkdir(exist_ok=True)
    prefix_lookup = pickle.load(open('res/prefix_lookup.pkl', 'rb'))
    replacements = []

    with open('res/replacements.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            replacements.append((re.compile(row[0]), row[1].replace("/s", " ")))

    rows = []
    empty = []

    for path in Path(DATA_DIR).glob('*.pdf'):
        pages = read_pdf(str(path))
        cover, _ = next(pages), next(pages)
        cover = [*process_cover(cover)]
        sl_no = 0

        for page in pages:
            for cell in crop_cells(page):
                sl_no += 1
                cell, voter_id = process_cell(cell)

                details = get_cell_main(cell)

                if not details:
                    empty.append([sl_no])
                    continue

                details.insert(0, str(sl_no))
                details.insert(1, voter_id)

                details = clean(details, prefix_lookup, replacements)
                rows.append(details + cover)

    # Write to CSV
    with open(f'{OUTPUT_DIR}/output.csv', 'w', encoding='utf-8',  newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)
        writer.writerows(empty)


if __name__ == '__main__':
    main()
