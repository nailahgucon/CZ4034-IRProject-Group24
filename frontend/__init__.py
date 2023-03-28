from flask import Flask, render_template

from frontend.views import home, all_records, pagination, crawling, filter, query

app = Flask(__name__)
app.config['SECRET_KEY'] = "A very secret key"


@app.errorhandler(404)
def not_found(error):
    print(error)
    return render_template('404.html'), 404


app.register_blueprint(home.home_bp)
app.register_blueprint(all_records.records_bp)
# app.register_blueprint(query.query_bp)
app.register_blueprint(pagination.pagination_bp)
app.register_blueprint(crawling.crawling_bp)
app.register_blueprint(filter.filter_bp)
app.register_blueprint(query.query_bp)
