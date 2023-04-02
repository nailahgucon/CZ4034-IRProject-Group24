from flask import Blueprint, render_template, request
import frontend.views.processes as records
import math
from frontend.views.processes import savedQuery

pagination_bp = Blueprint('pagination_bp', __name__, url_prefix='/pagination')


@pagination_bp.route('/')
def pagination():
    myRecords = records.records()
    results = myRecords.getDisplayRecords()
    myQuery = savedQuery.query()
    distinctStyle = myQuery.getStyle()

    totalPages = int(math.ceil(len(results) / 10))
    page = int(request.values.get("page"))
    if page < 1:
        page = 1
    start = page * 10 - 10
    end = 0 + page * 10
    if len(results) < end:
        displayResult = results[start : len(results)]
    else:
        displayResult = results[start:end]
    print("length of the results ", len(results))
    return render_template('results.html', docs=displayResult, distinctStyle=distinctStyle, current_page=page, total_pages=totalPages)