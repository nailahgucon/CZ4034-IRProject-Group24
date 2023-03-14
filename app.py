import json
from flask import Flask, render_template, url_for, request
import requests

app = Flask(__name__)

class records():
    docs = None
    @classmethod
    def store(cls, docs):
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
        if i["DateOfReview"] == date:
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
    query = request.values.get("content").replace(" ","%20")
    myRecords = records()
    # filter the existing data
    return render_template('index.html')
  else:
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)