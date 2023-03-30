import re
from flask import Blueprint, render_template, request, jsonify, redirect, url_for
# from frontend.views.processes import autocomplete
from typing import List
from backend.place import Place
from frontend.views.processes import autocomplete
from frontend.views.processes import spellcheck
import requests
import spacy

import pickle

from backend import Places
from backend import Response
# from backend import place
# from config import config
server_main:str = "http://localhost:8983/solr/reviews/select"
server_sub:str = "http://localhost:8983/solr/all_data/select"

nlp = spacy.load("en_core_web_sm")

# get all objects
with open("backend/data/place.pkl", 'rb') as inp:
    s = pickle.load(inp)

db = Places()
db.extend(s)

# o = db.calculate_nearest(db.place_list[0], 40)
# print(o)

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

NEAR_WORDS = ["near", "nearer", "close", "around"]
FAR_WORDS = ["far", "away", "further", "distant"]

CAT_EATERY = ['eateries', 'eatery', 'eat']
CAT_HOTEL = ['hotel', 'hotels', 'stay']

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
            # special query 1 - distance
                # e.g. eateries near Parkroyal Hotel
            dist = None
            category = None
            split_query = query_term.split(" ")
            for i in split_query:
                if i in NEAR_WORDS:
                    dist = 'near'
                    default_dist = 10.0
                elif i in FAR_WORDS:
                    dist = 'far'
                    default_dist = 10.0
                else:
                    pass
                if i in CAT_EATERY:
                    category = 'eatery'
                elif i in CAT_HOTEL:
                    category = 'hotel'
                else:
                    pass

            # standard query
            about_doc = nlp(query_term)
            entity = ' '.join([token.text for token in about_doc.ents])

            user_query = f"spellCheck:{entity}"
            kwargs.update({"q": user_query})

            results = requests.get(server_sub,
                                   params=kwargs).json()
            
            # ------------------------
            # 0 result | 1 results | +1 results
            # ------------------------
            # 0 result
                # typo
                # no match
            res = results.get("response").get("docs")
            if len(res) == 0:
                spellcheck_list = results.get("spellcheck").get("collations")
                if spellcheck_list:
                    correct_terms, typo_terms, collation_queries = spellcheck(spellcheck_list)
                    return render_template('queried.html',
                                        typos=collation_queries)
                else:
                    return render_template('404.html')
            # ------------------------
            # 1/1+ result
                # distance search
                    # adjust distance bar?
                # popularity top-k search
                        # display search page
            elif len(res) >= 1:
                names = []
                sorted_dist = {}
                if dist or category:
                    # get 1st place
                    p = db.get_place(res[0].get("Name")[0])
                    for i in db.place_list:
                        if i.name != p.name:
                            match_ = i.match(place=p,
                                    category=category,
                                    dist=dist,
                                    dist_value=default_dist)
                            if match_:
                                sorted_dist.update(match_)
                    sorted_dist = sorted(sorted_dist.items(), key=lambda x:x[1])
                for i in res:
                    names.append(i.get("Name")[0])
                return render_template('query_results.html',
                                       place_list=names, other_matches=sorted_dist)
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
    name_ = re.sub('[^0-9a-zA-Z]+', '_', name)
    query_name = re.sub('[^0-9a-zA-Z]+', ' ', name)
    name_ = name_.lower()
    kwargs.update({"q": f"spellCheck:{query_name}"})

    results = requests.get(server_main,
                            params=kwargs).json()
    results=results.get("response").get("docs")
    responses = []
    for i in results:
        style = i.get("Style")
        if style:
            style = style[0]
        responses.append(Response(
            name=i.get("Name")[0],
            style=style,
            category=i.get("Category")[0],
            star=i.get("Star")[0],
            date=i.get("Date")[0],
            rating=i.get("Rating")[0],
            reviewstitles=i.get("ReviewTitle")[0],
            reviews=i.get("Review")[0]
        ))
    return render_template("place.html", responses=responses)
