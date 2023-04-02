from flask import Flask, render_template, request
from flask import Blueprint, render_template
import subprocess
import os

crawling_bp = Blueprint('crawling_bp', __name__, url_prefix='/crawling')

@crawling_bp.route("/", methods=['GET'])
def crawling():
    # call crawling function here
    subprocess.call(['python', os.getcwd() + '\\crawling\\crawl_eateries_links.py'])
    subprocess.call(['python', os.getcwd() + '\\crawling\\crawl_hotels_links.py'])
    subprocess.call(['python', os.getcwd() + '\\crawling\\crawling_eateries.py'])
    subprocess.call(['python', os.getcwd() + '\\crawling\\crawling_hotels.py'])

    # call model prediction
    subprocess.call(['python', os.getcwd() + '\\sentiment\\model_predict.py'])

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

    return render_template("crawling.html")
