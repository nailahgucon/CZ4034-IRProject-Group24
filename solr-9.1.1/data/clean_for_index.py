# input: reviews_all.py

import pandas as pd
import csv
from typing import List

def clean(row:List[str]) -> List[str]:
    '''
    Given a row value
    ['val1', '['val2', 'val3']', ... , etc]
    
    Output cleaned row without list values
    '''
    new_list = []
    for val in row:
        if type(val) is list:
            if val[0]:
                val_ = []
                for u in val:
                # remove trailing and leading whitespaces
                    val_.append(u.strip())
                val_str = '|'.join(val_)
                val_str = val_str.replace("\'", '')
                new_list.append(val_str)
                continue
            else:
                new_list.append('')
                continue
        new_list.append(val)
    return new_list

def clean_csv(csv_file: str, special_col_name: List[str], new_csv: str):
    '''
    Cleans entire csv, reiterates through rows and
    calls clean()
    
    Writes the results in a csv
    '''
    data_df = pd.read_csv(csv_file)

    for i in special_col_name:
        data_df[i] = data_df[i].apply(lambda x: x[1:-1].split(','))
    
    with open(new_csv, 'w+') as f:
        writer = csv.writer(f)
        col_headers = [col.lower() for col in data_df.columns]
        writer.writerow(col_headers)
        for i in range(len(data_df.index)):
            row = list(data_df.iloc[i])
            row = clean(row)
            writer.writerow(row)
    return None

if __name__ == "__main__":
    csv_file = "reviews_all.csv"
    special_col_name = ['Style']
    new_csv = 'reviews.csv'

    clean_csv(csv_file, special_col_name, new_csv)
