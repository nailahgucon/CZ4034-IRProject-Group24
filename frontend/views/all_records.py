import json
import math
from flask import Flask, render_template, request
from datetime import datetime
import frontend.views.processes as records
import requests
from flask import Blueprint, render_template

records_bp = Blueprint('records_bp', __name__)

@records_bp.route('/getAllRecords', methods=['GET'])
def getAllrecords():
  # Build Solr query
  query = {
      "q": "*:*",
      "rows": 10000,
      "start": 0,
      "wt": "json",
  }
  URL = "http://localhost:8983/solr/reviews/select"
  
  # Send Solr query
  response = requests.get(URL, params=query)
  
  # Parse Solr results
  results = json.loads(response.text)["response"]["docs"]

  # save the results to records class, don't change myRecords and totalPages.
  myRecords = records.records()
  myRecords.store(results)
  
  # for pagination, only display 10 records
  totalPages = int(math.ceil(len(results) / 10))
  displayResult = results[0:10]
  
  return render_template('results.html', docs=displayResult, current_page=1, total_pages=totalPages)
  