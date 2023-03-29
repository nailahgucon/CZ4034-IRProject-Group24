import re
from flask import Blueprint, render_template, request, jsonify, redirect, url_for
# from frontend.views.processes import autocomplete
from typing import List
from backend.place import Place
from frontend.views.processes import autocomplete
from frontend.views.processes import spellcheck
import requests

import googlemaps

import pickle

from backend import Places
from backend import Response

# API_KEY = ''
# map_client = googlemaps.Client(API_KEY)
# from backend import place
# from config import config
server_main:str = "http://localhost:8983/solr/reviews/select"
server_sub:str = "http://localhost:8983/solr/all_data/select"

# get all objects
with open("backend/data/place.pkl", 'rb') as inp:
    s = pickle.load(inp)

db = Places()
db.extend(s)

o = db.calculate_nearest(db.place_list[0], 40)
print(o)

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
    # autocomplete for only hotel and eatery names
    availableTags = list(set(db.get_names))

    # Search page
    if request.method == 'GET':
        if page_name == "main":
            return render_template('home.html')
        elif page_name == "sub":
            # TODO: autocomplete done
            return render_template('query.html',
                                   availableTags=availableTags)
        else:
            return render_template('404.html')
    # results
    elif request.method == 'POST':
        if page_name == "main":
            return render_template('home.html')
        elif page_name == "sub":
            query_term = request.form.get('place_name')
            user_query = f"spellCheck:{query_term}"
            kwargs.update({"q": user_query})

            results = requests.get(server_sub,
                                   params=kwargs).json()
            
            # ------------------------
            # TODO: spellcheck done
            # check results for typos
            collation_queries = []
            spellcheck_list = results.get("spellcheck").get("collations")
            if spellcheck_list:
                correct_terms, typo_terms, collation_queries = spellcheck(spellcheck_list)

                print(f"Spellcheck: Error! Search instead for {collation_queries}?")
                return render_template('queried.html',
                                       typos=collation_queries)
            res = results.get("response").get("docs")
            # TODO: more than 1 results done
            if len(res) > 1:
                routes = []
                names = []
                for i in res:
                    name=i.get("Name")[0]
                    routes.append(f"http://127.0.0.1:5000/query/place/{name.replace(' ', '%20')}")
                    names.append(name)
                place_list = list(zip(names, routes))
                return render_template('query_results.html',
                                       place_list=place_list)
            # TODO: 1 result done
            elif len(res)==1:
                name = res[0].get("Name")[0]
                if name == query_term:
                    return redirect(url_for('query_bp.place', name=name))
                else:
                    routes = []
                    names = []
                    for i in res:
                        name=i.get("Name")[0]
                        routes.append(f"http://127.0.0.1:5000/query/place/{name.replace(' ', '%20')}")
                        names.append(name)
                    place_list = list(zip(names, routes))
                    return render_template('query_results.html',
                                        place_list=place_list)
            # TODO: no results done
            else:
                print("Could not find, try filtering instead?")
            return render_template('query.html',
                                   availableTags=availableTags)
        else:
            return render_template('404.html')

@query_bp.route('/place/<name>')
def place(name: str):
    '''
    creates a single place page
    '''
    # rname = name.replace("+", " ")
    # f = db.get_member(rname)
    # if f is None:
    #     return render_template("404.html")
    # Bar(db).plot(page=page, faculty=f,
    #              filename=config.FCITES_PATH,
    #              xaxis_title="Year",
    #              yaxis_title="No. of citations")
    
    name_ = re.sub('[^0-9a-zA-Z]+', '_', name)
    name_ = name_.lower()
    server_place:str = f"http://localhost:8983/solr/{name_}/select"
    # user_query = f"spellCheck:{query_term}"
    kwargs.update({"q": "*:*"})

    results = requests.get(server_place,
                            params=kwargs).json()
    results=results.get("response").get("docs")
    responses = []
    for i in results:
        responses.append(Response(
            name=i.get("Name")[0],
            style=i.get("Style")[0],
            category=i.get("Category")[0],
            star=i.get("Star")[0],
            date=i.get("Date")[0],
            rating=i.get("Rating")[0],
            reviewstitles=i.get("ReviewTitle")[0],
            reviews=i.get("Review")[0]
        ))
    # address = map_client.geocode(name)
    # print(address[0]['geometry'])
    return render_template("place.html", responses=responses)
