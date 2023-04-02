import json
import math
from flask import Flask, render_template, request
from datetime import datetime
import requests
import frontend.views.processes as records
from flask import Blueprint, render_template
from frontend.views.processes import savedQuery


filter_bp = Blueprint('filter_bp', __name__, url_prefix='/filter')

defaultURL = "http://localhost:8983/solr/reviews/select?q=%s&facet.field={!key=distinctStyle}distinctStyle&facet=on&rows=10000&wt=json&json.facet={distinctStyle:{type:terms,field:distinctStyle,limit:10000,missing:false,sort:{index:asc},facet:{}}}"


@filter_bp.route('/', methods=['GET'])
def filter():
  if request.method == 'GET':

    myRecords = records.records()
    myQuery = savedQuery.query()
    num = 0

    f = "&fq="

    # type cast the star filter
    style_filter = request.values.get('style')
    if style_filter:
       num+=1
       f+=f"Style:{style_filter}"

    category_filter = request.values.get('category')
    if category_filter:
      if num>0:
         f+=f"&Category:{category_filter}"
      else:
        f+=f"Category:{category_filter}"
      num+=1

    # type cast the star filter
    star_filter = request.values.get('star')
    formatted_star = None
    if star_filter:
      formatted_star = int(star_filter[0])
      if num>0:
         f+=f"&Star:{formatted_star}"
      else:
        f+=f"Star:{formatted_star}"
      num+=1

    # type cast the rating filter
    rating_filter = request.values.get('rating')
    formatted_rating = None
    if rating_filter:
      formatted_rating = int(rating_filter[0])
      if num>0:
        f+=f"&Rating:{formatted_rating}"
      else:
        f+=f"Rating:{formatted_rating}"
      num+=1

    # type cast the date filter
    start_date_filter = request.values.get('startDate')
    end_date_filter = request.values.get('endDate')
    print(start_date_filter)
    print(end_date_filter)
    print("____-")
    if start_date_filter and end_date_filter:
      if num>0:
        f+=f'&Date:["{start_date_filter}T00:00:00Z" TO "{end_date_filter}T00:00:00Z"]'
      else:
        f+=f'Date:["{start_date_filter}T00:00:00Z" TO "{end_date_filter}T00:00:00Z"]'    
      num+=1


    URL = defaultURL%(myQuery.getQuery()+f)

    # print("URL ", URL)
    # Send Solr query
    response = requests.get(URL)

    # Parse Solr results
    rawData = json.loads(response.text)
    if rawData["response"]["numFound"] != 0:
      results = rawData["response"]["docs"]
      distinctStyle = rawData["facets"]["distinctStyle"]["buckets"]
      for i in distinctStyle:
        i["val"] = i["val"].replace("[",'').replace("]",'').replace("'",'')
      myQuery.storeStyle(distinctStyle)

      # save the results to records class
      myRecords.store(results)
    else:
      results = []
      distinctStyle = myQuery.getStyle()

    # for pagination, only display 10 records
    totalPages = int(math.ceil(rawData["response"]["numFound"] / 10))
    displayResult = results[0:10]

    return render_template('results.html', docs = displayResult, distinctStyle=distinctStyle, current_page=1, total_pages=totalPages)
  else:
    return render_template('home.html')
