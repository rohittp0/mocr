import csv
import itertools
import pickle

import Levenshtein
import numpy as np

from res.lacs import LAC


def create_lookup_table():
    with open('res/prefix.txt', 'r') as f:
        my_list = [line.strip().lower() for line in f.readlines()]

    lookup_table = {}
    for combination in itertools.product('abcdefghijklmnopqrstuvwxyz1234567890', repeat=3):
        my_string = ''.join(combination)
        closest_match = None
        closest_distance = None
        for word in my_list:
            distance = Levenshtein.distance(my_string, word)
            if closest_distance is None or distance < closest_distance:
                closest_match = word
                closest_distance = distance
        lookup_table[my_string] = closest_match

    with open('res/prefix_lookup.pkl', 'wb') as f:
        pickle.dump(lookup_table, f)


def create_lac_booth():
    rows = []
    with open("res/booth.csv", "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] and row[1] and row[2]:
                rows.append((int(row[0]), int(row[1]), row[2]))

    array = [[lac] for lac in LAC]
    rows.sort(key=lambda x: (x[0], x[1]))

    for row in rows:
        array[row[0] - 1].append(row[2].strip())

    np_array = np.empty((len(array), max([len(c) for c in array]) + 1), dtype=object)

    for i in range(len(array)):
        for j in range(len(array[i])):
            np_array[i, j] = array[i][j]

    np.save("res/lac_booth.npy", np_array, allow_pickle=True)


if __name__ == '__main__':
    create_lac_booth()
