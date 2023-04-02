import os
import subprocess

import requests
from flask import Blueprint, Flask, render_template, request

from backend.crawl import crawl_single

crawling_bp = Blueprint('crawling_bp', __name__, url_prefix='/crawling')

@crawling_bp.route("/", methods=['GET'])
def crawling():
    # call crawling function here
    link = request.form.get('link')
    # e.g. link = "https://www.tripadvisor.com/Restaurant_Review-g294265-d21391354-Reviews-French_Fold_Telok_Ayer-Singapore.html"
    response = requests.get(link)
    if response.status_code != 200:
        return render_template('404.html')
    else:
        completed: bool = crawl_single(link)
    # TODO: render the template
    if completed:
        return "Successfully added!"
    else:
        return "Could not be added...Page already exist!"

    # subprocess.call(['python', os.getcwd() + '\\crawling\\crawl_eateries_links.py'])
    # subprocess.call(['python', os.getcwd() + '\\crawling\\crawl_hotels_links.py'])
    # subprocess.call(['python', os.getcwd() + '\\crawling\\crawling_eateries.py'])
    # subprocess.call(['python', os.getcwd() + '\\crawling\\crawling_hotels.py'])

    # call model prediction
    # subprocess.call(['python', os.getcwd() + '\\sentiment\\model_predict.py'])

    # delete documents
    # import xml.etree.ElementTree as ET

    # URL = "http://localhost:8983/api/collections/reviews/update?commit=true"

    # header = {"Content-Type": "text/xml"}

    # root = ET.Element("delete")
    # query = ET.SubElement(root, "query")
    # query.text = "*:*"
    # xml_payload = ET.tostring(root)

    # # print(xml_payload)
    # # Send the HTTP request to Solr
    # response = requests.get(URL, headers=header, data=xml_payload)

    # return render_template("crawling.html")
