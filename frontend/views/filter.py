import json
import math
from flask import Flask, render_template, request
from datetime import datetime
import frontend.views.processes as records
import requests
from flask import Blueprint, render_template

from typing import List

import pickle

from backend import Places

with open("backend/data/place.pkl", 'rb') as inp:
    s = pickle.load(inp)

db = Places()
db.extend(s)

places: List[str] = db.get_names

filter_bp = Blueprint('filter_bp', __name__, url_prefix='/filter')

@filter_bp.route('/', methods=['GET'])
def filter():
  if request.method == 'GET':
    print(db.get_unique_styles())
            # ['Restaurants', 'Residential Neighborhood', 'Bay View', 'Vegetarian Friendly', 'Marina View', 'Gluten Free Options', 'Centrally Located', 'Mid-range', 'Vegan Options', 'Trendy', 'Family', 'Park View']
            
    myRecords = records.records()

    # type cast the rating filter
    rating_filter = request.values.get('rating')
    formatted_rating = None
    if rating_filter:
      formatted_rating = int(rating_filter[0])

    # type cast the date filter
    start_date_filter = request.values.get('startDate')
    end_date_filter = request.values.get('endDate')
    formatted_start_date = None
    formatted_end_date = None
    if start_date_filter and end_date_filter:
      start_date_obj = datetime.strptime(start_date_filter, '%Y-%m-%d')
      end_date_obj = datetime.strptime(end_date_filter, '%Y-%m-%d')
      formatted_start_date = datetime.strptime(start_date_obj.strftime('%B %d, %Y'), '%B %d, %Y')
      formatted_end_date = datetime.strptime(end_date_obj.strftime('%B %d, %Y'), '%B %d, %Y')

    # actual filter
    if formatted_rating and formatted_start_date and formatted_end_date:
      result = myRecords.filterByDateAndRating(formatted_start_date, formatted_end_date, formatted_rating)
    elif formatted_rating:
      result = myRecords.filterByRating(formatted_rating)
    elif formatted_start_date and formatted_end_date:
      result = myRecords.filterByDate(formatted_start_date, formatted_end_date)   
    else:
      result = myRecords.getAllRecords() 
    
    totalPages = int(math.ceil(len(result) / 10))
    displayResult = result[0:10]

    return render_template('results.html', docs = displayResult, current_page=1, total_pages=totalPages)
  else:
    return render_template('home.html')