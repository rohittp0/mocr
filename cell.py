import re

import cv2
import numpy as np
import pytesseract


def crop_cells(image: np.ndarray):
    # Apply thresholding to create a binary image
    _, thresh = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Find the contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    # Initialize a list to store the cell images
    coords = []

    # Iterate over the contours
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)

        if w / h < 2 or w / h > 3 or cv2.contourArea(contour) < 1000:
            continue

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


def get_cell_main(cell: np.ndarray):
    text = pytesseract.image_to_string(cell, lang='mal')
    text = text.replace("\u200c", "").replace("\u200d", "")

    labels = ["പേര", "വീട്ടു", "വീടു", "വീരു", "നമ്പര്", "പ്രായം", "ലിംഗം", ":", "സ്തീ", "പുരുഷന്‍"]

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
        return []

    name_regex = r".*പേ[രര്‍]്?\s*:?\s*"
    house_regex = r".*വീട്ടു\s?(നമ്പര്‍|നമ്പര)്?\s*:?\s*"
    relation_map = {
        r"ഭ[രര്‍]്?ത്താ?വ്?": "ഭർത്താവ്",
        r"അച.*(ൻ|ന)": "അച്ഛൻ",
        r"അമ": "അമ്മ",
    }

    name = re.sub(name_regex, "", fields[0])
    husband = re.sub(name_regex, "", fields[1])
    house = re.sub(house_regex, "", fields[2])
    gender = "സ്ത്രീ" if ("സ്തീ" in fields[3] or "സ്ത്രീ" in fields[3]) else "പുരുഷൻ"

    age = cell[int(cell.shape[0] // 2.5):, int(cell.shape[1] // 4.5):int(cell.shape[1] // 3)]
    age = pytesseract.image_to_string(age, lang='eng')

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


def process_cell(cell):
    # Apply thresholding to create a binary image
    _, thresh = cv2.threshold(cell, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    voter_id = ""

    for con in contours:
        x_i, y_i, w_i, h_i = cv2.boundingRect(con)

        if w_i / h_i > 1 or cv2.contourArea(con) < 1000:
            continue

        voter_id_cell = cell[:, x_i:]
        voter_id = pytesseract.image_to_string(voter_id_cell, lang='eng').split("\n")[0]

        cell = cell[int(y_i // 2):, :x_i - 5]
        break

    return cell, voter_id
