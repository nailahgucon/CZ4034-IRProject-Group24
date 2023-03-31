import re
from flask import Blueprint, render_template, request
from typing import List
from backend.place import Place
from frontend.views.processes import autocomplete
from frontend.views.processes import spellcheck
import requests
import spacy

import pickle

from backend import Places
from backend import Response

server_main:str = "http://localhost:8983/solr/reviews/select"
server_sub:str = "http://localhost:8983/solr/all_data/select"
# proximity search
# http://localhost:8983/solr/reviews/select?q=Review:%22lovely%20food%22~10
# http://localhost:8983/solr/reviews/select?q=ReviewTitle:%22Good%20service%20dessert%22~10
# http://localhost:8983/solr/reviews/select?q=ReviewTitle:%22Good%20service%22%20dessert

# boosting terms
# http://localhost:8983/solr/reviews/select?q=Review:%22lovely%20food%22^4%20ambience


nlp = spacy.load("en_core_web_sm")

# get all objects
with open("backend/data/place.pkl", 'rb') as inp:
    s = pickle.load(inp)

db = Places()
db.extend(s)

# TODO rank query results
# TODO top-k "best eateries/best hotels"

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
          'rows': 10,
          }

NEAR_WORDS = ["near", "nearer", "close", "around"]

CAT_EATERY = ['eateries', 'eatery', 'eat']
CAT_HOTEL = ['hotel', 'hotels', 'stay']

FILTER_WORDS_TOP = ["best", "top", "popular", "high", "highest"]
FILTER_WORDS_BOT = ["worst", "worse", "least", "bad", "bottom"]

WORDS = NEAR_WORDS+CAT_EATERY+CAT_HOTEL+FILTER_WORDS_TOP+FILTER_WORDS_BOT

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
        if page_name == "main":
            return render_template('home.html')
        elif page_name == "sub":
            query_term = request.form.get('place_name')
            # query 1 - exact match                          # done
                # e.g. Parkroyal | parkroyal    
            # query 2 - spelling check                       # done
                # e.g. parkroyil
            # special query 1 - distance                     # done
                # e.g. eateries near Parkroyal Hotel    
            # special query 2 - top-k                        # done
                # e.g. top eateries near Parkroyal Hotel 
                # e.g. top 5 eateries near Parkroyal  
                # e.g. top eateries 
            # special query 3 - More like this
            category = None
            rank = None
            k = 100
            geo_filter = False
            split_query = query_term.split(" ")
            res2 = []
            sort_field = ''
            for i in split_query:
                if i in NEAR_WORDS:
                    geo_filter = True
                    default_dist = 1.0
                if i in CAT_EATERY:
                    category = 'eatery'
                elif i in CAT_HOTEL:
                    category = 'hotel'
                else:
                    pass

                if i in FILTER_WORDS_TOP:
                    rank = 'asc'
                    kwargs.update({"rows":"5"})
                elif i in FILTER_WORDS_BOT:
                    rank = 'desc'
                    kwargs.update({"rows":"5"})
                else:
                    pass
            new_query = ' '.join([i for i in split_query if (i not in WORDS)])
            if rank:
                sort_field += "Star desc,"
            # exact matches
            if not new_query:
                user_query = "*:*"
            else:
                if len(new_query.split()) == 1:
                    user_query = f"spellCheck:{new_query}"
                else:
                    user_query = f"spellCheck:\"{new_query}\""
            kwargs.update({"q": user_query,
                           "sort": sort_field},
                         )
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
            elif len(res) >= 1:
                names = []
                names2 = []
                if geo_filter:
                    # get 1st place
                    sort_field += "geodist() asc"
                    lat = res[0].get("lat")
                    lon = res[0].get("lon")
                    kwargs.update({"q": "*:*",
                                   "fq": "{!geofilt}",
                                   "sfield": "location",
                                   "pt":f"{lat},{lon}",
                                   "d":default_dist,
                                   "sort": sort_field,
                                   "fl":"{!func}geodist(),Name",
                                   },
                                )
                    res2 = requests.get(server_sub,
                                           params=kwargs).json()
                    
                    res2 = res2.get("response").get("docs")
                    for i in res2[1:]:
                        names2.append([i.get("Name")[0], i.get("{!func}geodist()")])
                if category:
                    kwargs.update({"q": "*:*",
                                   "fq": f"Category:{category}",
                                   "sort": sort_field,
                                   },
                                )
                    res2 = requests.get(server_sub,
                                           params=kwargs).json()
                    
                    res = res2.get("response").get("docs")
                for i in res:
                    names.append([i.get("Name")[0], i.get("Star")])
                return render_template('query_results.html',
                                       place_list=names, other_matches=names2)
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
    kwargs.update({"q": f"spellCheck:{query_name}",
                   "sort": ''})
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
