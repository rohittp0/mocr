import csv
import pickle
import re
from pathlib import Path

import cv2
import numpy as np
import pytesseract

DATA_DIR = 'data'
OUTPUT_DIR = 'output'

sharpen_filter = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])


def crop_cells(image_path):
    # Load the image and convert it to grayscale
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply thresholding to create a binary image
    _, thresh = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Find the contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Initialize a list to store the cell images
    coords = []

    # Iterate over the contours
    for contour in contours:
        # Check if the contour has required area
        if 120000 > cv2.contourArea(contour) < 90000:
            continue

        # Get the rectangle that contains the contour
        x, y, w, h = cv2.boundingRect(contour)

        cell = image[y + 3:y + h - 2, x + 3:x + w - 2]
        coords.append((x, y, cell))

    coords.sort(key=lambda c: (c[1] // 10, c[0]))
    d_min = 30

    for i, cord in enumerate(coords):
        skip = False
        for j in range(i + 1, len(coords)):
            if abs(cord[0] - coords[j][0]) < d_min and abs(cord[1] - coords[j][1]) < d_min:
                skip = True
                break
            if abs(cord[0] - coords[j][0]) > d_min:
                break

        if not skip:
            yield cord[2]


def process_cell(cell):
    # Apply thresholding to create a binary image
    _, thresh = cv2.threshold(cell, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    voter_id = ""

    for con in contours:
        x_i, y_i, w_i, h_i = cv2.boundingRect(con)

        if w_i / h_i > 1 or cv2.contourArea(con) < 1000:
            continue

        voter_id_cell = cell[:, x_i:]
        voter_id = pytesseract.image_to_string(voter_id_cell, lang='eng').split("\n")[0]

        cell = cell[:, :x_i - 5]
        break

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        # Check if the contour has required area
        if cv2.contourArea(contour) < 5000 or w / h < 3:
            continue

        cell = cell[y + h + 2:, :]

        return cell, voter_id

    return cell, ''


def get_cell_main(cell: np.ndarray):
    text = pytesseract.image_to_string(cell, lang='mal')
    text = text.replace("\u200c", "").replace("\u200d", "")

    labels = ["പേര", "വീട്ടു", "നമ്പര്", "പ്രായം", "ലിംഗം", ":", "സ്തീ", "പുരുഷന്‍"]

    previous = ""
    fields = []

    for line in text.split("\n"):
        if any([label in line for label in labels]):
            if previous:
                fields.append(previous)
            previous = line
        else:
            previous += " " + line

    fields.append(previous)

    if len(fields) < 4:
        print("Missing fields: ", fields)
        return

    name_regex = r".*പേ[രര്‍]്?\s*:?\s*"
    house_regex = r".*വീട്ടു\s?(നമ്പര്‍|നമ്പര)്?\s*:?\s*"
    age_regex = r".*പ്രായം\s*:?\s*"
    relation_map = {
        r"ഭ[രര്‍]്?ത്താ?വ്?": "ഭർത്താവ്",
        r"അച.*(ൻ|ന)": "അച്ഛൻ",
        r"അമ": "അമ്മ",
    }

    name = re.sub(name_regex, "", fields[0])
    husband = re.sub(name_regex, "", fields[1])
    house = re.sub(house_regex, "", fields[2])
    age = re.sub(age_regex, "", fields[3]).split("ല")[0]
    gender = "സ്ത്രീ" if "സ്തീ" in fields[3] else "പുരുഷൻ"

    relation = fields[1].split(":")[0]
    for k, v in relation_map.items():
        if re.match(k, fields[1]):
            relation = v
            break

    ret = [
        name.strip(),
        relation.strip(),
        husband.strip(),
        house.strip(),
        age.strip(),
        gender
    ]

    return ret


def clean(details, prefix_lookup):
    sl_no, voter_id, name, relation, husband, house, age, gender = details

    voter_id = re.sub(r'\W+', '', voter_id)
    voter_id = prefix_lookup[voter_id[:3].lower()] + voter_id[3:].upper().replace("O", "0")
    voter_id = voter_id[:3] + voter_id[-7:]

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
    with open(f'{OUTPUT_DIR}/output.csv', 'w', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(rows)


if __name__ == '__main__':
    main()
