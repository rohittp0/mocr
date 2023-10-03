import re
from typing import List, Tuple

import cv2
import numpy as np
import pytesseract

from utils import show


def get_rois(cover: np.ndarray) -> List[np.ndarray]:
    _, thresh = cv2.threshold(cover, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    iw, ih = cover.shape[::-1]
    max_area = iw * ih / 10

    rois = [None, None]
    y_min = 1000000

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        area = cv2.contourArea(contour)

        ratio = w / h

        if 500 > area or area > max_area:
            continue

        if 3 > ratio or x > iw * 0.05 or ratio > 27 or ih * 0.07 < y < ih * 0.4 or y > ih * 0.6:
            continue

        if 8 < ratio < 26 and y < y_min:
            y_min = y
            rois[0] = cover[y:y + h, x:x + w]
        elif y > ih / 2.2 and 3 < ratio < 5:
            rois[1] = cover[y:y + h, x:x + w]

    return rois


def name_and_no(roi: np.ndarray) -> Tuple[str, str]:
    txt = pytesseract.image_to_string(roi, lang='mal').split("\n")[0]
    txt = re.sub(r'[:-]', ' ', txt).replace("\u200c", "").replace("\u200d", "")

    no_match = re.search(r'\d{1,3}|\d\s*\d?\s*\d?', txt)
    no = no_match.group().replace(" ", "") if no_match else ''

    name = re.sub(r'\d', '', txt)

    return no, name.strip()


def process_lac(lac: np.ndarray) -> Tuple[str, str]:
    lac[:, :int(lac.shape[1] / 1.75)] = 255
    return name_and_no(lac)


def process_booth(booth):
    y1, y2 = int(booth.shape[0] / 4), int(booth.shape[0] / 2)
    booth = booth[y1:y2, :]

    return name_and_no(booth)


def process_cover(cover: np.ndarray) -> Tuple[str, str, str, str]:
    rois = get_rois(cover)

    ret = ["", "", "", ""]

    if rois[0] is not None:
        ret[0], ret[1] = process_lac(rois[0])

    if rois[1] is not None:
        ret[2], ret[3] = process_booth(rois[1])

    return ret[0], ret[1], ret[2], ret[3]
