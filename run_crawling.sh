#!/bin/bash
cd "CZ4034 Crawling"
python crawl_eateries_links.py
echo "eatery links done"
python crawl_hotels_links.py
echo "hotel links done"
python crawling_eateries.py
echo "eatery reviews done"
python crawling_hotels.py
echo "hotel reviews done"