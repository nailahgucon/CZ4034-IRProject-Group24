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
    return render_template("crawling.html")