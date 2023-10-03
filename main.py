import csv
import pickle
import re
from pathlib import Path
from typing import List, Tuple, Pattern, AnyStr

import Levenshtein

from cell import crop_cells, process_cell, get_cell_main
from cover import process_cover
from pdf import read_pdf
from res.lacs import LAC

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

    voter_id = re.sub(r'\W+', '', voter_id)
    prefix, number = voter_id[:3].lower(), voter_id[-7:].upper().replace("O", "0")

    voter_id = prefix_lookup[prefix] + number if len(prefix) == 3 else ''

    age_match = re.search(r'\d{2}|\d\s+\d', age)
    age = age_match.group().replace(" ", "") if age_match else ''

    name, husband = re.sub(r'\d+', '', name), re.sub(r'\d+', '', husband)
    name, husband, house = replace(name, husband, house, replacements=replacements)

    return [sl_no, voter_id.upper(), name, relation, husband, house, age, gender]


def match_lac(name):
    closest_match = -1
    closest_distance = int(1e9)

    for i in range(len(LAC)):
        distance = Levenshtein.distance(name, LAC[i])

        if distance < closest_distance:
            closest_match = i
            closest_distance = distance

    return LAC[closest_match], str(closest_match + 1)


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

    for path in Path(DATA_DIR).glob('*.pdf'):
        pages = read_pdf(str(path))
        cover, _ = next(pages), next(pages)
        cover = replace(*process_cover(cover), replacements=replacements)
        cover[0], cover[1] = match_lac(cover[1])
        sl_no = 0

        for page in pages:
            for cell in crop_cells(page):
                sl_no += 1
                cell, voter_id = process_cell(cell)

                details = get_cell_main(cell)

                if not details:
                    empty.append([sl_no, voter_id, *([""] * 6), *cover])

                details.insert(0, str(sl_no))
                details.insert(1, voter_id)

                details = clean(details, prefix_lookup, replacements)
                rows.append(details + cover)

                print(f'\rSL No: {sl_no}', end="")
        print(f'\nProcessed {path}')

    # Write to CSV
    with open(f'{OUTPUT_DIR}/output.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    with open(f'{OUTPUT_DIR}/empty.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(empty)


if __name__ == '__main__':
    main()
