import json
import os
import pickle
from typing import List
import csv

# from config import config

from place import Place


def load_in(dir: str) -> List[Place]:
    """
    Read in records as Faculty Members
    """
    all_places = []
    for f in os.listdir(dir):
        if f.endswith("data.csv"):
            with open(os.path.join(dir, f), 'r') as out:
                # info = json.load(out)
                csvreader = csv.reader(out)
                next(csvreader, None)
                for row in csvreader:
                    # -- append as objects
                    # print(row[0])
                    # print(row[1])
                    # print(row[2])
                    # print(row[3])
                    # print("_____")
                    all_places.append(
                        Place(name=row[0],
                              category=row[1],
                              style=row[2],
                              star=row[3],
                              ))
    return all_places





