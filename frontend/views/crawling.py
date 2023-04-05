from flask import Blueprint, render_template, request

from backend.crawl import crawl_single

crawling_bp = Blueprint('crawling_bp', __name__, url_prefix='/crawling')

# TODO: render the for output response

@crawling_bp.route("/", methods=['GET', 'POST'])
def crawling():
    if request.method == 'POST':
        link = request.form.get('URL')
        # e.g. link = 
        # http://www.tripadvisor.com/Restaurant_Review-g294265-d21391354-Reviews-French_Fold_Telok_Ayer-Singapore.html
        completed: bool = crawl_single(link)
        if completed:
            return render_template('crawling.html', complete=completed)
        else:
            incomplete = True
            return render_template('crawling.html', incomplete=incomplete)

    return render_template('crawling.html')
