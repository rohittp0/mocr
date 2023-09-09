from pathlib import Path

import cv2
import numpy as np
import easyocr
import pytesseract

from utils import show

DATA_DIR = 'data'
OUTPUT_DIR = 'output'

en_reader = easyocr.Reader(['en'])
sharpen_filter = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])


def crop_cells(image_path):
    # Load the image and convert it to grayscale
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply thresholding to create a binary image
    _, thresh = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Find the contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Initialize a list to store the cell images
    cells = []

    # Iterate over the contours
    for contour in contours:
        # Check if the contour has required area
        if 120000 > cv2.contourArea(contour) < 90000:
            continue

        # Get the rectangle that contains the contour
        x, y, w, h = cv2.boundingRect(contour)

        cell = thresh[y + 3:y + h - 2, x + 3:x + w - 2]

        cons, _ = cv2.findContours(cell, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        for con in cons:
            x_i, y_i, w_i, h_i = cv2.boundingRect(con)

            if w_i / h_i > 1 or cv2.contourArea(con) < 1000:
                continue

            cell = image[y + 1:y + h, x + 1:x + w][:, :x_i - 5]
            break

        cells.append(cell)

    return cells


def process_cell(cell):
    # Apply thresholding to create a binary image
    _, thresh = cv2.threshold(cell, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Find the contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        # Check if the contour has required area
        if cv2.contourArea(contour) < 5000:
            continue

        # Get the rectangle that contains the contour
        x, y, w, h = cv2.boundingRect(contour)

        sl_no = cell[y:y + h, x:x + w]
        cell = cell[y + h + 2:, :]

        # Create a sharpening kernel
        kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])

        # Apply the sharpening kernel to the image
        sl_no = cv2.filter2D(sl_no, -1, kernel)

        sl_no_text = "".join(en_reader.readtext(sl_no, detail=0))

        return cell, sl_no_text.strip()

    return cell, ''


def get_cell_main(cell: np.ndarray):
    cell = cv2.resize(cell, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
    cell = cv2.filter2D(cell, -1, sharpen_filter)
    cell = cv2.copyMakeBorder(cell, 10, 10, 10, 10, cv2.BORDER_CONSTANT)
    text = pytesseract.image_to_string(cell, lang='mal')

    show(cell)
    print(text)

    return text


def main():
    Path(OUTPUT_DIR).mkdir(exist_ok=True)

    for path in Path(DATA_DIR).glob('*.png'):
        cells = crop_cells(str(path))

        for i, cell in enumerate(cells):
            cell, sl_no = process_cell(cell)
            try:
                sl_no = int(sl_no)
            except ValueError:
                continue

            cv2.imwrite(f'{OUTPUT_DIR}/{sl_no}.png', cell)
            # text = get_cell_main(cell)


if __name__ == '__main__':
    main()
