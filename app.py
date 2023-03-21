import json
from flask import Flask, render_template, request
from datetime import datetime
import requests

from spellcheck import spellcheck
from mlt import mlt
from autocomplete import autocomplete

app = Flask(__name__)

class records():
    docs = None
    @classmethod
    def store(cls, docs):
      print("document ", docs[0]["Title"][0])
      cls.docs = docs
    
    def filterByRating(self, rating):
      result = []
      for i in self.docs:
        if i["Rating"] == rating:
          result.append(i)
      return result
    
    def filterByDate(self, start_date, end_date):
      result = []
      for i in self.docs:
        date = datetime.strptime(i["DateOfReview"][0], '%B %d, %Y')
        
        if date >= start_date and date <= end_date:
          result.append(i)
      return result
    
    def filterByDateAndRating(self,start_date, end_date,rating):
      result = []
      for i in self.docs:
        date = datetime.strptime(i["DateOfReview"][0], '%B %d, %Y')
        if date >= start_date and date <= end_date and i["Rating"] == rating:
          result.append(i)
      return result
    
    def getAllRecords(self):
      return self.docs

@app.route('/', methods=['GET'])
def index():
  queryContent = "*"
  filed = "*"
  # Build Solr query
  query = {
      "q": "*:*",
      "fq": f"{filed}:{queryContent}",
      "rows": 10,
      "start": 0,
      "spellcheck.build": "true",
      "spellcheck.reload": "true",
      "spellcheck": "true",
      "wt": "json"
  }
  URL = "http://localhost:8983/solr/reviews/select"
  
  # Send Solr query
  response = requests.get(URL, params=query)
  
  # Parse Solr results
  results = json.loads(response.text)["response"]["docs"]

  myRcords = records()
  myRcords.store(results)

  return render_template('index.html', docs=results)

@app.route('/query', methods=['GET'])
def query():
  if request.method == 'GET':
    queryContent = request.values.get("content").replace(" ","%20")
    filed = "Review"

    # Build Solr query
    query = {
        "q": "*:*",
        "fq": f"{filed}:{queryContent}",
        "rows": 10,
        "start": 0,
        "spellcheck.build": "true",
        "spellcheck.reload": "true",
        "spellcheck": "true",
        "wt": "json",
    }
    URL = "http://localhost:8983/solr/reviews/select"
    
    # Send Solr query
    response = requests.get(URL, params=query)

    # check results for typos
    res = {}
    spellcheck_list = results.get("spellcheck").get("collations")
    if spellcheck_list:
        correct_terms, typo_terms = spellcheck(spellcheck_list)
        for correct_term in correct_terms:
            res2 = query(col_name, correct_term, server, **kwargs)
            res.update(res2)
    else:
        res.update(results)
    
    # check results for suggestions
    suggtexts = autocomplete(results)

    # Parse Solr results
    results = json.loads(response.text)["response"]["docs"]
    

    myRcords = records()
    myRcords.store(results)
    return render_template('index.html', docs=results)
  else:
    return render_template('index.html')
  

@app.route('/filter', methods=['GET'])
def filter():
  if request.method == 'GET':

    myRecords = records()
    rating_filter = request.values.get('rating')
    formatted_rating = None
    if rating_filter:
      formatted_rating = int(rating_filter[0])

    start_date_filter = request.values.get('startDate')
    end_date_filter = request.values.get('endDate')
    formatted_start_date = None
    formatted_end_date = None

    if start_date_filter and end_date_filter:
      start_date_obj = datetime.strptime(start_date_filter, '%Y-%m-%d')
      end_date_obj = datetime.strptime(end_date_filter, '%Y-%m-%d')
      formatted_start_date = datetime.strptime(start_date_obj.strftime('%B %d, %Y'), '%B %d, %Y')
      formatted_end_date = datetime.strptime(end_date_obj.strftime('%B %d, %Y'), '%B %d, %Y')

    if formatted_rating and formatted_start_date and formatted_end_date:
      result = myRecords.filterByDateAndRating(formatted_start_date, formatted_end_date, formatted_rating)
    elif formatted_rating:
      result = myRecords.filterByRating(formatted_rating)
    elif formatted_start_date and formatted_end_date:
      result = myRecords.filterByDate(formatted_start_date, formatted_end_date)   
    else:
      result = myRecords.getAllRecords() 
    
    return render_template('index.html', docs = result)
  else:
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)