from flask import Blueprint, render_template, request, jsonify
# from frontend.views.processes import autocomplete
from typing import List
from frontend.views.processes import autocomplete
from frontend.views.processes import spellcheck
import requests

import pickle

from backend import Places
# from backend import place
# from config import config
server:str = "http://localhost:8983/solr/reviews/select"
# get all objects
with open("backend/data/place.pkl", 'rb') as inp:
    s = pickle.load(inp)

db = Places()
db.extend(s)

places: List[str] = db.get_names
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

query_bp = Blueprint('query_bp', __name__, url_prefix='/query')


@query_bp.route('/<page_name>', methods=['GET', 'POST'])
def query(page_name):
    if request.method == 'GET':
        if page_name == "main":
            return "kiv"
        elif page_name == "sub":
            # search bar for only hotel and eatery names
            # TODO add availableTags as variable to javascript query.html
            availableTags = list(set(db.get_names))
            search = request.args.get('selected-input')
            print(f"The search term is: {search}")
            # user_query = f"spellCheck:{search}"
            # kwargs.update({"q": user_query})

            # results = requests.get(server,
            #                       params=kwargs).json()
            # suggtexts = autocomplete(results)

            # print(f"Autocomplete: Are you looking for {suggtexts}?")
            
            return render_template('query.html')
        else:
            return "kiv"
    elif request.method == 'POST':
        if page_name == "main":
            return "kiv"
        elif page_name == "sub":
            query_term = request.form.get('restaurant_name')
            user_query = f"spellCheck:{query_term}"
            kwargs.update({"q": user_query})

            results = requests.get(server,
                                params=kwargs).json()
            
            # ------------------------
            # check results for typos
            collation_queries = []
            spellcheck_list = results.get("spellcheck").get("collations")
            if spellcheck_list:
                correct_terms, typo_terms, collation_queries = spellcheck(spellcheck_list)

                print(f"Spellcheck: Error! Search instead for {collation_queries}?")
            
            print(results)
            
            # TODO rendering template
            return render_template('queried.html', docs=results,
                                   typos=collation_queries)
        else:
            return "kiv"

      
    #jsonify(matching_results=suggtexts)
        # place_list = list(zip(db.place_list, db.links()))
        # faculty_list = sorted(faculty_list, key=lambda x: x[0].name)
        # return render_template('home.html', faculty_list=faculty_list)
        # bellow is the query to solr, need update to handle spell check,
        # the variable suggtexts is used for spell suggestion to the user. 
        

        # # check results for typos
        # spellcheck_list = results.get("spellcheck").get("collations")
        # if spellcheck_list:
        #     correct_terms, typo_terms, collation_queries = spellcheck(spellcheck_list)

        # print(f"Spellcheck: Error! Search instead for {collation_queries}?")

        # # check results for suggestions
        # # kiv - need AJAX for updating
        # suggtexts = autocomplete(results)

        # print(f"Autocomplete: Are you looking for {suggtexts}?")

        # # more like this
        # out = mlt(results)
        # print(f"More like this: {out}, matching on the field {mlt_field}")

        # # # Parse Solr results
        # # results = json.loads(response.text)["response"]["docs"]
        # # save the results to records class, don't change myRecords and totalPages.
        # myRecords = records.records()
        # myRecords.store(results)
        
        # # for pagination, only display 10 records
        # totalPages = int(math.ceil(len(results) / 10))
        # displayResult = results[0:10]


        # return render_template('results.html', docs=displayResult, current_page=1, total_pages=totalPages)
    
    # else:
    # return render_template('home.html')