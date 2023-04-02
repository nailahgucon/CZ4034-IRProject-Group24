import json
import math
import re
from flask import Blueprint, render_template, request
from frontend.views.processes import savedQuery, spellcheck, records
# from frontend.views.processes.records as records
import requests
from frontend.views.processes import plot
import pickle

import io
from flask import Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

server_main:str = "http://localhost:8983/solr/reviews/select"
server_sub:str = "http://localhost:8983/solr/all_data/select"
# proximity search
# http://localhost:8983/solr/reviews/select?q=Review:%22lovely%20food%22~10
# http://localhost:8983/solr/reviews/select?q=ReviewTitle:%22Good%20service%20dessert%22~10
# http://localhost:8983/solr/reviews/select?q=ReviewTitle:%22Good%20service%22%20dessert

# boosting terms
# http://localhost:8983/solr/reviews/select?q=Review:%22lovely%20food%22^4%20ambience


# TODO clean up code

places = requests.get(server_sub, params={
    "q":"*:*",
    "rows": "500",
    "fl": "Name"
}).json()
places = places.get("response").get("docs")
places = [i.get("Name") for i in places]


NEAR_WORDS = ["near", "nearer", "close", "around"]

CAT_EATERY = ['eateries', 'eatery', 'eat']
CAT_HOTEL = ['hotel', 'hotels', 'stay']

FILTER_WORDS_TOP = ["best", "top", "popular", "high", "highest"]
FILTER_WORDS_BOT = ["worst", "worse", "least", "bad", "bottom"]

WORDS = NEAR_WORDS+CAT_EATERY+CAT_HOTEL+FILTER_WORDS_TOP+FILTER_WORDS_BOT

defaultURL = "http://localhost:8983/solr/reviews/select?q=%s&facet.field={!key=distinctStyle}distinctStyle&facet=on&rows=10000&wt=json&json.facet={distinctStyle:{type:terms,field:distinctStyle,limit:10000,missing:false,sort:{index:asc},facet:{}}}"

query_bp = Blueprint('query_bp', __name__, url_prefix='/query')


@query_bp.route('/<page_name>', methods=['GET', 'POST'])
def query(page_name):

    # Search page
    if request.method == 'GET':
        if page_name == "main":
            return render_template('results.html')
        elif page_name == "sub":
            return render_template('query.html',
                                   availableTags=places)
        else:
            return render_template('404.html')
    # results
    elif request.method == 'POST':
        kwargs = {}
        if page_name == "main":
            # query 1 - proximity searches
                # e.g. "price service"~10  -- search for "price" and "service"
                #                          -- within 10 words of each other in a document,
            # query 2 - boosting terms
                # e.g. food^2 service      -- term "food" to be more relevant,
                #                          -- boost it by adding the ^ symbol
                #                          -- along with the boost factor.
            query_term = request.form.get('place_name')
            split_query = query_term.split(" ")

            # spellcheck only on review texts
            if len(split_query) >1:
                pass
            else:
                kwargs.update({'spellcheck': 'true',})
            user_query = f"Review:{query_term}"

            kwargs.update({"q": user_query,},)
            results = requests.get(server_main,
                                   params=kwargs).json()
            res = results.get("response").get("docs")
            myRecords = records()
            myRecords.store(res)
            
            # for pagination, only display 10 records
            totalPages = int(math.ceil(len(res) / 10))
            displayResult = res[0:10]
            
            return render_template('results.html', docs=displayResult, current_page=1, total_pages=totalPages)
  
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
            # special query 3 - More like this              # done
            category = None
            rank = None
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
                for i in res:
                    names.append([i.get("Name"), i.get("Star")])
                if geo_filter and category:
                    sort_field = "geodist() asc,Star desc"
                    lat = res[0].get("lat")
                    lon = res[0].get("lon")
                    field_query = f"(Category:'{category}')" + " AND {!geofilt}"
                    kwargs.update({"q": "*:*",
                                   "fq": field_query,
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
                        names2.append([i.get("Name"), i.get("{!func}geodist()")])
                elif geo_filter:
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
                        names2.append([i.get("Name"), i.get("{!func}geodist()")])
                elif category:
                    kwargs.update({"q": "*:*",
                                   "fq": f"Category:{category}",
                                   "sort": sort_field,
                                   },
                                )
                    res2 = requests.get(server_sub,
                                           params=kwargs).json()
                    
                    res = res2.get("response").get("docs")
                
                return render_template('query_results.html',
                                       place_list=names, other_matches=names2)
            return "Uh oh, could not find any results, please try again."
        else:
            return render_template('404.html')

@query_bp.route('/place/<name>')
def place(name: str):
    '''
    creates a single place page
    '''
    kwargs = {
          'spellcheck': 'true',
          }
    name_ = re.sub('[^0-9a-zA-Z]+', '_', name)
    query_name = re.sub('[^0-9a-zA-Z]+', ' ', name)
    name_ = name_.lower()
    kwargs.update({"q": f"spellCheck:\"{query_name}\"",
                   "mlt":"true",
                   "mlt.fl": "Style",
                   "mlt.match.include": "true",
                   "mlt.mindf":"0",
                   "mlt.mintf":"0",
                   })
    results_main = requests.get(server_sub,
                            params=kwargs).json()
    results_mlt=results_main.get("moreLikeThis")
    results_mlt=results_mlt.get(list(results_mlt)[0]).get("docs")
    results_main=results_main.get("response").get("docs")
    lat = results_main[0].get("lat")
    lon = results_main[0].get("lon")
    default_dist = 10
    

    kwargs = {
          'spellcheck': 'true',
          }
    kwargs.update({"q": f"spellCheck:\"{query_name}\"",
                   })
    results_reviews = requests.get(server_main,
                            params=kwargs).json()
    
    results_reviews=results_reviews.get("response").get("docs")

    sort_field = "geodist() asc"

    kwargs = {
          'spellcheck': 'true',
          }
    kwargs.update({"q": "*:*",
                    "fq": "{!geofilt}",
                    "sfield": "location",
                    "pt":f"{lat},{lon}",
                    "d":default_dist,
                    "sort": sort_field,
                    "fl":"location,Name",
                    },
                )
    res2 = requests.get(server_sub,
                            params=kwargs).json()
    
    res2 = res2.get("response").get("docs")
    plot(res2)
    
    return render_template("place.html", results_main=results_main[0],
                           results_reviews=results_reviews,
                           results_mlt=results_mlt)

@query_bp.route('/plot_png')
def plot_png():
    figx = pickle.load(open('frontend/views/plots/dist.fig.pickle', 'rb'))
    output = io.BytesIO()

    FigureCanvas(figx).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')
