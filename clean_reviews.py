import csv
import ast
import os
from config.config import review_header

cleaned_file = "crawling/finalised_files/reviews.csv"

# Open the file to save the review
if not os.path.exists(cleaned_file):
    with open(cleaned_file, "w+", encoding="utf-8", newline='') as f:
        csvWriter = csv.writer(f)
        if os.stat(cleaned_file).st_size == 0:
            csvWriter.writerow(review_header)
            
with open("crawling/finalised_files/reviews_combined_predicted.csv", "r", encoding="utf-8") as f:
    reader_obj = csv.reader(f)
    next(reader_obj)
    for row in reader_obj:
        new_row = row[2:]
        new_data = ast.literal_eval(new_row[2])
        new_data = "|".join(new_data)
        new_row = row[2:4]
        new_row.append(new_data)
        new_row.extend(row[5:])
        with open(cleaned_file, 'a', encoding="utf-8", newline='') as f:
            csvWriter = csv.writer(f)
            csvWriter.writerow(new_row)
