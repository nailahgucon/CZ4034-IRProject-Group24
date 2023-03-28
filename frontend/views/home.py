import pickle

from flask import Blueprint, render_template

home_bp = Blueprint('home_bp', __name__)


@home_bp.route('/', methods=['GET'])
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