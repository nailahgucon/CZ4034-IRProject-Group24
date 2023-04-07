# CZ4034-Project

# Installations
https://solr.apache.org/downloads.html

1. Install binary package
2. clone repo 
`gh repo clone nailahgucon/CZ4034-IRProject-Group24`

## Launch Solr in SolrCloud Mode
Windows
solr.cmd start -c

MacOS/Linux
solr start -c

## Delete all Data
XML:
https://stackoverflow.com/questions/7722508/how-to-delete-all-data-from-solr-and-hbase/7722558#7722558 


## Step-by-Step: Run code

1. Ensure SOLR is installed. Refer to : https://solr.apache.org/downloads.html
2. Generate Google Maps API key for geocoding purposes here (FOC): https://console.cloud.google.com/apis/credentials
3. Clone this repository
4. Move downloaded solr-*.tgz file from Downloads into root folder `CZ4034-IRProject-Group24`
5. Unzip solr-*.tgz file
6. Copy/Cut/Move the files in `solr-9.1.1/server/solr/configsets` into `solr-*/server/solr/configsets`<br>
Directory structure:<br>
CZ4034-IRProject-Group24<br>
|--> backend<br>
..|--> data<br>
..|--> crawl.py<br>
..|--> sentiment.py<br>
|--> config<br>
|--> crawling<br>
..|--> chromedriver_win32<br>
..|--> finalised_files<br>
  ..|--> crawl_eateries_links.py<br>
  ...<br>
|--> frontend<br>
  ..|--> static<br>
  ..|--> templates<br>
  ..|--> views<br>
|--> sentiment<br>
  ..|--> additional_data<br>
  ..|--> models<br>
  ..|--> model_predict.py<br>
|--> solr-*<br>
  ..|--> bin<br>
  ..|--> docker<br>
  ..|--> server<br>
    ....|--> solr<br>
      ......|--> configsets<br>
        ........|--> _default<br>
  ...<br>

7. (Optional) Create virtual environment
`virtualenv /path/to/new/virtual/environment` OR `python -m venv /path/to/new/virtual/environment`
8. In console, `pip install -r requirements.txt`
> This can take some time.
9. If Google API key is activated, go into folder config/config.py and replace:<br>
`API_KEY = ''  # your API key here`<br>
with your API key<br>
e.g. `API_KEY = 'Aqiihud7627883mndsq12'`
10. Open a new command prompt/terminal

MACOS/LINUX commands
***
11. Navigate to solr-* directory. E.g. `cd ./CZ4034-IRProject-Group24/solr-9.1.1`<br>
12. Start solr: `bin/solr start`<br>
13. Create reviews solr core: `bin/solr create -c reviews -d reviews`<br>
14. Create all_data solr core: `bin/solr create -c all_data -d all_data`<br>
15. Post data into reviews solr core: `bin/post -c reviews ./CZ4034-IRProject-Group24/backend/data/reviews.csv`<br>
16. Post data into reviews solr core: `bin/post -c reviews ./CZ4034-IRProject-Group24/backend/data/all_data.csv`<br>
***
17. Run code in console using command `python app.py`<br>
> This can take some time to build up the sentiment analysis model
18. Open google chrome/safari etc navigate to link: http://127.0.0.1:5000<br>

***
19. To stop solr: `bin/solr stop` MACOS/LINUX
