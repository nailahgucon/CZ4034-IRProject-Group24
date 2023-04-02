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