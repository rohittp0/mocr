import random
from typing import List, Generator

from PIL import Image, ImageDraw, ImageFont
from PIL.ImageFont import FreeTypeFont

size = (379 // 2, 165 // 2)


def draw_text(text: List[str], font: FreeTypeFont, draw: ImageDraw):
    x, y = 10, 10

    for line in text:
        draw.text((x, y), line, font=font, fill='black')
        y += font.getsize(line)[1]  # Move to the next line


def get_text() -> Generator[List[str], None, None]:
    names = open('names.txt', 'r', encoding='utf-8')
    husbands = open('husbands.txt', 'r', encoding='utf-8')
    house = open('house.txt', 'r', encoding='utf-8')

    husband_labels = [
        'അച്ഛൻ്റെ',
        'ഭർത്താവിൻ്റെ',
        'അമ്മയുടെ',
    ]

    gender_values = [
        'പുരുഷൻ',
        'സീ',
    ]

    for name, husband, house in zip(names.readlines(), husbands.readlines(), house.readlines()):
        h_label = random.choice(husband_labels)
        g_value = random.choice(gender_values)

        name, husband, house = name.strip().split("\n"), husband.strip().split("\n"), house.strip().split("\n")

        yield [
            f'പേര് : {name[0]}',
            *name[1:],
            f'{h_label} പേര്: {husband[0]}',
            *husband[1:],
            f'വീട്ടു നമ്പർ : {house[0]}',
            *house[1:],
            f'പ്രായം : {random.randint(18, 99)} ലിംഗം : {g_value}',
        ]


def main():
    bg = Image.new('gray', size, 255)
    font = ImageFont.truetype('path/to/malayalam-font.ttf', size=40)

    texts = []

    for i, text in enumerate(get_text()):
        draw = ImageDraw.Draw(bg)
        draw_text(text, font, draw)

        texts.append("~".join(text))
        bg.save(f'output/{i}.png')

    with open('output.txt', 'w', encoding='utf-8') as f:
        f.write("\n".join(texts))


if __name__ == '__main__':
    main()
