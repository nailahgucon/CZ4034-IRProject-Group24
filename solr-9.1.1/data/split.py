'''
This is only used to generate all_data.csv
after reviews.csv is created.
'''

import csv
from typing import List
import googlemaps

API_KEY = ''  # your API key here
map_client = googlemaps.Client(API_KEY)

reviews_path = 'solr-9.1.1/data/reviews.csv'
header = ['Name','Category','Style','Star','Long','Lat']
data_path = "solr-9.1.1/data/all_data2.csv"
current_name = ''


def append_coord(current_row:List[str]):
    '''
    given a single row in reviews.csv,
    output a new row with coordinates
    appended.
    '''
    address = map_client.geocode(row[0])
    if address:
        coordinates = address[0]['geometry'].get("location")
        lat = coordinates.get('lat')
        long = coordinates.get('lng')
        new_row = current_row[:4]
        new_row.extend([lat, long])
        return new_row
    return None


with open(reviews_path, 'r') as f:
    csv_reader = csv.reader(f, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            with open(data_path, 'w+') as out:
                writer = csv.writer(out, delimiter=',')
                writer.writerow(header)
        else:
            if current_name != row[0]:
                current_name = row[0]
                with open(data_path, 'a') as out:
                    writer = csv.writer(out, delimiter=',')
                    new_row = append_coord(row, row[0])
                    if new_row:
                        writer.writerow(new_row)
            line_count += 1


