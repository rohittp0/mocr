from typing import Generator

import cv2
import fitz  # PyMuPDF
import numpy as np


def pix_to_image(pix):
    img_bytes = np.frombuffer(pix.samples, dtype=np.uint8)
    img = img_bytes.reshape(pix.height, pix.width, pix.n)
    return img


def read_pdf(path: str) -> Generator[np.ndarray, None, None]:
    for page in fitz.open(path):
        image = pix_to_image(page.get_pixmap(matrix=fitz.Matrix(2, 2)))
        yield cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
