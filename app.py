import json
import math
from flask import Flask, render_template, request
from datetime import datetime
import records
import requests

from spellcheck import spellcheck
from mlt import mlt
from autocomplete import autocomplete

app = Flask(__name__)

# test query

server:str = "http://localhost:8983/solr/reviews/select"
col_name:str = "spellCheck"  # or any other copyfields
query_term:str = "parkroyal"
mlt_field = "Style"
kwargs = {'spellcheck.build': "true",
          'spellcheck.reload': "true",
          'spellcheck': 'true',
          'mlt':'true',
          'mlt.fl': mlt_field,
          'mlt.interestingTerms':'details',
          'mlt.match.include': 'true',
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
  query = {
      "q": "*:*",
      "rows": 10000,
      "start": 0,
      "spellcheck.build": "true",
      "spellcheck.reload": "true",
      "spellcheck": "true",
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
  
@app.route('/query', methods=['GET'])
def query():
  if request.method == 'GET':

    # bellow is the query to solr, need update to handle spell check, the variable suggtexts is used for spell suggestion to the user. 

    user_query = f"{col_name}:{query_term}"
    kwargs.update({"q": user_query})

    results = requests.get(server,
                           params=kwargs).json()

    # check results for typos
    spellcheck_list = results.get("spellcheck").get("collations")
    if spellcheck_list:
        correct_terms, typo_terms, collation_queries = spellcheck(spellcheck_list)

    print(f"Spellcheck: Error! Search instead for {collation_queries}?")

    # check results for suggestions
    # kiv - need AJAX for updating
    suggtexts = autocomplete(results)

    print(f"Autocomplete: Are you looking for {suggtexts}?")

    # more like this
    out = mlt(results)
    print(f"More like this: {out}, matching on the field {mlt_field}")

    # # Parse Solr results
    # results = json.loads(response.text)["response"]["docs"]
    # save the results to records class, don't change myRecords and totalPages.
    myRecords = records.records()
    myRecords.store(results)
    
    # for pagination, only display 10 records
    totalPages = int(math.ceil(len(results) / 10))
    displayResult = results[0:10]


    return render_template('results.html', docs=displayResult, current_page=1, total_pages=totalPages)
  else:
    return render_template('home.html')

@app.route('/pagination')
def pagination():
    myRecords = records.records()
    results = myRecords.getDisplayRecords()
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
    return render_template('results.html', docs=displayResult, current_page=page, total_pages=totalPages)


@app.route('/filter', methods=['GET'])
def filter():
  if request.method == 'GET':

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

@app.route("/crawling", methods=['GET'])
def crawling():
    # call crawling function here

    return render_template("crawling.html")

if __name__ == "__main__":
    app.run(debug=True)