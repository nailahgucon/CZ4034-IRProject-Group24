import json
import math
import subprocess
import os
from flask import Flask, render_template, request
from datetime import datetime
import records
import requests
import savedQuery

from spellcheck import spellcheck
from mlt import mlt
from autocomplete import autocomplete

app = Flask(__name__)

# test query
defaultURL = "http://localhost:8983/solr/reviews/select?q=%s&facet.field={!key=distinctStyle}distinctStyle&facet=on&rows=10000&wt=json&json.facet={distinctStyle:{type:terms,field:distinctStyle,limit:10000,missing:false,sort:{index:asc},facet:{}}}"
server:str = "http://localhost:8983/solr/reviews/select"
col_name:str = "spellCheck"  # or any other copyfields
query_term:str = "Review"
mlt_field = "Rating"
kwargs = {'spellcheck.build': "true",
          'spellcheck.reload': "true",
          'spellcheck': 'true',
          'mlt':'true',
          'mlt.fl': mlt_field,
          'mlt.interestingTerms':'details',
          'mlt.match.include': 'false',
          'mlt.mintf': '0',
          'mlt.mindf': '0',
          }

mlt_url = "http://localhost:8983/solr/reviews/mlt"

@app.route('/', methods=['GET'])
def home():

  # # Build Solr query
  # query = {
  #     "q": "*:*",
  #     "fq": "*:*",
  #     "rows": 100000,
  #     "start": 0,
  #     "mlt":"true",
  #     "spellcheck.build": "true",
  #     "spellcheck.reload": "true",
  #     "spellcheck": "true",
  #     "wt": "json"
  # }
  # URL = "http://localhost:8983/solr/reviews/select"
  
  # # Send Solr query
  # response = requests.get(URL, params=query)
  
  # # Parse Solr results
  # results = json.loads(response.text)["response"]["docs"]

  # # myRcords = records.records()
  # # myRcords.store(results)
  
  return render_template('home.html')

@app.route('/getAllRecords', methods=['GET'])
def getAllrecords():
  # Build Solr query
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

  # save the results to records class, don't change myRecords and totalPages.
  myRecords = records.records()
  myRecords.store(results)
  
  # for pagination, only display 10 records
  totalPages = int(math.ceil(len(results) / 10))
  displayResult = results[0:10]
  
  return render_template('results.html', docs=displayResult, distinctStyle=distinctStyle, current_page=1, total_pages=totalPages)

@app.route('/query', methods=['GET'])
def query():
  if request.method == 'GET':

    # bellow is the query to solr, need update to handle spell check, the variable suggtexts is used for spell suggestion to the user. 

    query_term = request.values.get("content")
    # Build Solr query
    myQuery = savedQuery.query()
    myQuery.storeQuery(f"spellCheck:{query_term}")
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

    # save the results to records class
    myRecords = records.records()
    myRecords.store(results)
    
    # for pagination, only display 10 records
    totalPages = int(math.ceil(len(results) / 10))
    displayResult = results[0:10]


    return render_template('results.html', docs=displayResult, distinctStyle=distinctStyle, current_page=1, total_pages=totalPages)
  else:
    return render_template('home.html')

@app.route('/pagination')
def pagination():
    myRecords = records.records()
    results = myRecords.getDisplayRecords()
    myQuery = savedQuery.query()
    distinctStyle = myQuery.getStyle()

    totalPages = int(math.ceil(len(results) / 10))
    page = int(request.values.get("page"))
    if page < 1:
        page = 1
    start = page * 10 - 10
    end = 0 + page * 10
    if len(results) < end:
        displayResult = results[start : len(results)]
    else:
        displayResult = results[start:end]
    print("length of the results ", len(results))
    return render_template('results.html', docs=displayResult, distinctStyle=distinctStyle, current_page=page, total_pages=totalPages)


@app.route('/filter', methods=['GET'])
def filter():
  if request.method == 'GET':

    myRecords = records.records()
    myQuery = savedQuery.query()
    f = "fq:"

    # type cast the star filter
    style_filter = request.values.get('style')

    # type cast the star filter
    star_filter = request.values.get('star')
    formatted_star = None
    if star_filter:
      formatted_star = int(star_filter[0])
      f+=f"Star:{formatted_star} "

    # type cast the rating filter
    rating_filter = request.values.get('rating')
    formatted_rating = None
    if rating_filter:
      formatted_rating = int(rating_filter[0])
      f+=f"Rating:{formatted_rating} "

    # type cast the date filter
    start_date_filter = request.values.get('startDate')
    end_date_filter = request.values.get('endDate')
    formatted_start_date = None
    formatted_end_date = None
    if start_date_filter and end_date_filter:
      start_date_obj = datetime.strptime(start_date_filter, '%Y-%m-%d')
      end_date_obj = datetime.strptime(end_date_filter, '%Y-%m-%d')
      formatted_start_date = datetime.strptime(start_date_obj.strftime('%Y-%m-%dT%H:%M:%SZ'),'%Y-%m-%dT%H:%M:%SZ')
      formatted_end_date = datetime.strptime(end_date_obj.strftime('%Y-%m-%dT%H:%M:%SZ'),'%Y-%m-%dT%H:%M:%SZ')
      f+=f'Date:["{formatted_start_date}" TO "{formatted_end_date}"]'
    
    print("filter ", f)
    
    # URL = defaultURL%(myQuery.getQuery())

    # actual filter
    # if formatted_rating and formatted_start_date and formatted_end_date and style_filter and formatted_star:
    #    pass
    # elif formatted_rating and formatted_start_date and formatted_end_date:
    #   result = myRecords.filterByDateAndRating(formatted_start_date, formatted_end_date, formatted_rating)
    # elif formatted_rating:
    #   result = myRecords.filterByRating(formatted_rating)
    # elif formatted_start_date and formatted_end_date:
    #   result = myRecords.filterByDate(formatted_start_date, formatted_end_date)   
    # else:
    result = myRecords.getAllRecords() 
    
    totalPages = int(math.ceil(len(result) / 10))
    displayResult = result[0:10]

    return render_template('results.html', docs = displayResult, current_page=1, total_pages=totalPages)
  else:
    return render_template('home.html')

@app.route("/crawling", methods=['GET'])
def crawling():
    # call crawling function here
    subprocess.call(['python', os.getcwd() + '\\crawling\\crawl_eateries_links.py'])
    subprocess.call(['python', os.getcwd() + '\\crawling\\crawl_hotels_links.py'])
    subprocess.call(['python', os.getcwd() + '\\crawling\\crawling_eateries.py'])
    subprocess.call(['python', os.getcwd() + '\\crawling\\crawling_hotels.py'])

    # delete documents
    # import xml.etree.ElementTree as ET

    # URL = "http://localhost:8983/api/collections/reviews/update?commit=true"

    # header = {"Content-Type": "text/xml"}

    # root = ET.Element("delete")
    # query = ET.SubElement(root, "query")
    # query.text = "*:*"
    # xml_payload = ET.tostring(root)

    # # print(xml_payload)
    # # Send the HTTP request to Solr
    # response = requests.get(URL, headers=header, data=xml_payload)

    return render_template("crawling.html")

if __name__ == "__main__":
    app.run(debug=True)