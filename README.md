# CZ4034-Project

## Launch Solr in SolrCloud Mode
Windows
solr.cmd start -c

MacOS/Linux
solr start -c

## Create core/database
solr create -c *Name_of_database*
 >> Create with configset
bin/solr create -c reviews -d reviews_configs

## Upload data
bin/solr delete -c reviews
