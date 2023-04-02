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

## Launch Solr (recommended)

Navigate into solr-9.1.1 dir or whichever
<br>
MacOS/Linux
bin/solr start

## Stop Solr (recommended)
Navigate into solr-9.1.1 dir or whichever
<br>
MacOS/Linux
bin/solr stop

## Create core/database
solr create -c *Name_of_database*

**Create with configset**
bin/solr create -c reviews -d reviews
bin/solr create -c all_data -d all_data

## Upload data
bin/post -c reviews data/reviews.csv
bin/post -c all_data data/all_data.csv


## Delete all Data
XML:
https://stackoverflow.com/questions/7722508/how-to-delete-all-data-from-solr-and-hbase/7722558#7722558 

## To start this app, run:
1. Ensure you are in the root folder e.g. CZ4034-IRProject-Group24 then
<br>
python app.py

Also, make sure to start solr first
