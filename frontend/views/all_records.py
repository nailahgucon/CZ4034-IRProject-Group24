import json
import math
from flask import Flask, render_template, request
from datetime import datetime
import frontend.views.processes as records
import requests
from flask import Blueprint, render_template
from frontend.views.processes import savedQuery


records_bp = Blueprint('records_bp', __name__)

defaultURL = "http://localhost:8983/solr/reviews/select?q=%s&facet.field={!key=distinctStyle}distinctStyle&facet=on&rows=10000&wt=json&json.facet={distinctStyle:{type:terms,field:distinctStyle,limit:10000,missing:false,sort:{index:asc},facet:{}}}"

@records_bp.route('/getAllRecords', methods=['GET'])
def getAllrecords():
  
  myQuery = savedQuery.query()
  myQuery.storeQuery("*:*")
  URL = defaultURL%(myQuery.getQuery())

  # Send Solr query
  response = requests.get(URL)

  # Parse Solr results
  rawData = json.loads(response.text)
  results = rawData["response"]["docs"]
  distinctStyle = rawData["facets"]["distinctStyle"]["buckets"]
  for i in distinctStyle:
    i["val"] = i["val"].replace("[",'').replace("]",'').replace("'",'')
  myQuery.storeStyle(distinctStyle)
  # print("distinct style ", myQuery.getStyle())

  # save the results to records class, don't change myRecords and totalPages.
  myRecords = records.records()
  myRecords.store(results)

  # for pagination, only display 10 records
  totalPages = int(math.ceil(rawData["response"]["numFound"] / 10))
  displayResult = results[0:10]

  return render_template('results.html', docs=displayResult, distinctStyle=distinctStyle, current_page=1, total_pages=totalPages)