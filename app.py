import json
from flask import Flask, render_template, request
from datetime import datetime
import requests

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
    
    def filterByDate(self, date):
      result = []
      for i in self.docs:
        if i["DateOfReview"][0] == date:
          result.append(i)
      return result
    
    def filterByDateAndRating(self,date,rating):
      result = []
      for i in self.docs:
        if i["DateOfReview"] == date and i["Rating"] == rating:
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

    date_filter = request.values.get('date')
    formatted_date = None
    if date_filter:
      date_obj = datetime.strptime(date_filter, '%Y-%m-%d')
      formatted_date = date_obj.strftime('%B %d, %Y')

    if formatted_rating and formatted_date:
      result = myRecords.filterByDateAndRating(formatted_date, formatted_rating)
    elif formatted_rating:
      result = myRecords.filterByRating(formatted_rating)
    elif formatted_date:
      result = myRecords.filterByDate(formatted_date)   
    else:
      result = myRecords.getAllRecords() 
    
    return render_template('index.html', docs = result)
  else:
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)