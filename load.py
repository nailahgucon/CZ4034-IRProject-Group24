from pathlib import Path

import os
import pickle
from typing import List
import csv

from backend import Place

ROOT = str(Path().absolute())
DATA_FILE = ROOT + "/backend/data"


def load_in(dir: str) -> List[Place]:
    """
    Read in records as Faculty Members
    """
    all_places = []
    for f in os.listdir(dir):
        if f.endswith(".csv"):
            with open(os.path.join(dir, f), 'r') as out:
                # info = json.load(out)
                csvreader = csv.reader(out)
                next(csvreader, None)
                for row in csvreader:
                    # -- append as objects
                    all_places.append(
                        Place(name=row[0],
                              category=row[1],
                              style=row[2],
                              star=float(row[3]),
                              coordinates=(float(row[5]), float(row[4]))
                              ))
    return all_places

def save_object(obj, filename):
    with open(filename, 'wb') as outp:  # Overwrites any existing file.
        pickle.dump(obj, outp, pickle.HIGHEST_PROTOCOL)

if __name__ == "__main__":
    db: List[Place] = load_in(DATA_FILE)
    save_object(db, f'{DATA_FILE}/place.pkl')
