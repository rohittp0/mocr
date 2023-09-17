import csv
import pickle
import re
from pathlib import Path

from cell import crop_cells, process_cell, get_cell_main

DATA_DIR = 'data'
OUTPUT_DIR = 'output'


def clean(details, prefix_lookup):
    sl_no, voter_id, name, relation, husband, house, age, gender = details

    voter_id = re.sub(r'\W+', '', voter_id)
    prefix, number = voter_id[:3].lower(), voter_id[-7:].upper().replace("O", "0")

    voter_id = prefix_lookup[prefix] + number if len(prefix) == 3 else ''

    age_match = re.search(r'\d{2}|\d\s+\d', age)
    age = age_match.group().replace(" ", "") if age_match else ''

    return [sl_no, voter_id, name, relation, husband, house, age, gender]


def main():
    Path(OUTPUT_DIR).mkdir(exist_ok=True)
    prefix_lookup = pickle.load(open('prefix_lookup.pkl', 'rb'))

    rows = []
    sl_no = 0

    for path in Path(DATA_DIR).glob('*.png'):
        for cell in crop_cells(str(path)):
            sl_no += 1
            cell, voter_id = process_cell(cell)

            details = get_cell_main(cell)

            if not details:
                continue

            details.insert(0, str(sl_no))
            details.insert(1, voter_id)

            details = clean(details, prefix_lookup)
            rows.append(details)

    # Write to CSV
    with open(f'{OUTPUT_DIR}/output.csv', 'w', encoding='utf-8',  newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)


if __name__ == '__main__':
    main()
