import json
from flask import Flask, render_template, request
from datetime import datetime
import requests

from spellcheck import spellcheck
from mlt import mlt
from autocomplete import autocomplete

app = Flask(__name__)

# test query

server:str = "http://localhost:8983/solr/reviews/select"
col_name:str = "spellCheck"  # or any other copyfields
query_term:str = "Sparrow"
mlt_field = "Type"
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

  # Build Solr query
  query = {
      "q": "*:*",
      "fq": "*:*",
      "rows": 100000,
      "start": 0,
      "mlt":"true",
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

  # return "nice" 
  render_template('index.html', docs=results)

@app.route('/query', methods=['GET', 'POST'])
def query():
  if request.method == 'GET':
    # queryContent = request.values.get("content").replace(" ","%20")
    # filed = "Review"
    user_query = f"{col_name}:{query_term}"
    kwargs.update({"q": user_query})

    '''
    example of kwargs(additional params on top of query):
    {'spellcheck.build': "true",
     'spellcheck.reload': "true",
     'spellcheck': "true"}
    '''
    response = requests.get(server,
                           params=kwargs)

    
    results = json.loads(response.text)
    
    # check results for typos
    spellcheck_list = results.get("spellcheck").get("collations")
    if spellcheck_list:
        correct_terms, typo_terms, collation_queries = spellcheck(spellcheck_list)
        print("Are these what you mean?")
        # if more than 1 correct terms
        for terms in collation_queries:
          term_ = terms.split('\n')
          # takes the odd indices
          term = ' '.join([
            term_[i] for i in range(len(term_))
            if i % 2 == 1])
          print(term)
          # # can re-query
          # res2 = query(col_name, correct_term, server, **kwargs)
          # res.update(res2)
    # else:
    #     typo_res.update(results)
    
    # check results for suggestions
    suggtexts = autocomplete(results)
    print(f"Your query is {query_term}, are you looking for {suggtexts}?")

    # more like this
    out = mlt(results)
    print(f"output for more like this is {out}")

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