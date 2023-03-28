import json
import math
from flask import Flask, render_template, request
from datetime import datetime
import frontend.views.processes as records
import requests
from flask import Blueprint, render_template

crawling_bp = Blueprint('crawling_bp', __name__, url_prefix='/crawling')

@crawling_bp.route("/", methods=['GET'])
def crawling():
    # call crawling function here

    return render_template("crawling.html")