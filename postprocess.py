import csv
import re


def run():
    replacements = []

    with open('res/replacements.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            replacements.append((re.compile(row[0]), row[1].replace("/s", " ")))

    cleaned = []

    with open('output/output.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        cleaned.append(next(reader))

        for i, row in enumerate(reader):
            if not row[2] or row[2] == '':
                cleaned.append(row)
                continue

            for pattern, replacement in replacements:
                row[2] = pattern.sub(replacement, row[2])

            cleaned.append(row)
            print(f'\rRow No: {i}', end="")

    with open('output/cleaned.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(cleaned)


if __name__ == '__main__':
    run()
