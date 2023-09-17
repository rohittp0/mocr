import itertools
import pickle

import Levenshtein


def create_lookup_table():
    with open('prefix.txt', 'r') as f:
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

    with open('prefix_lookup.pkl', 'wb') as f:
        pickle.dump(lookup_table, f)


if __name__ == '__main__':
    create_lookup_table()
