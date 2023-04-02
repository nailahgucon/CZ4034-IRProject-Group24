# default number of scraped pages
num_page = 1

# Local
review_file = "backend/data/reviews.csv"
all_data_file = "backend/data/all_data.csv"
# Remote
remote_reviews = 'http://localhost:8983/solr/reviews'
remote_data = 'http://localhost:8983/solr/all_data'

server_sub = f"{remote_data}/select"
server_main = f"{remote_reviews}/select"

et = ["Restaurants", "Fast Food",
      "Quick Bites","Dessert",
      "Coffee & Tea","Bakeries",
      "Bars & Pubs","Specialty Food Market",
      "Delivery Only"]
dr = ["Halal", "Vegetarian Friendly",
      "Vegan Options", "Kosher",
      "Gluten Free Options"]
review_header = ["Name","Category","Style",
                 "Star","Date", "Rating",
                 "ReviewTitle", "Review",
                 "Sentiment"]
all_data_header = ["Name","Category","Style",
                   "Star","lat","lon"]

API_KEY = 'AIzaSyCEl2l5qFEY-Qf1_VjelMlooH5PjTgOdhM'  # your API key here


NEAR_WORDS = ["near", "nearer", "close", "around"]

CAT_EATERY = ['eateries', 'eatery', 'eat']
CAT_HOTEL = ['hotel', 'hotels', 'stay']

FILTER_WORDS_TOP = ["best", "top", "popular", "high", "highest"]
FILTER_WORDS_BOT = ["worst", "worse", "least", "bad", "bottom"]

WORDS = NEAR_WORDS+CAT_EATERY+CAT_HOTEL+FILTER_WORDS_TOP+FILTER_WORDS_BOT


defaultURL = "http://localhost:8983/solr/reviews/select?q=%s&facet.field={!key=distinctStyle}distinctStyle&facet=on&rows=10000&wt=json&json.facet={distinctStyle:{type:terms,field:distinctStyle,limit:10000,missing:false,sort:{index:asc},facet:{}}}"

