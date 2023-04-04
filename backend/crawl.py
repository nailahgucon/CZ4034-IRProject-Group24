import csv
import logging
import os
import time
from datetime import datetime

import googlemaps
import pysolr
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By

from sentiment import model_predict

from config.config import *

rsolr = pysolr.Solr(remote_reviews, always_commit=True)
dsolr = pysolr.Solr(remote_data, always_commit=True)

map_client = googlemaps.Client(API_KEY)

# Open the file to save the review
if not os.path.exists(review_file):
    with open(review_file, "w+", encoding="utf-8", newline='') as f:
        csvWriter = csv.writer(f)
        if os.stat(review_file).st_size == 0:
            csvWriter.writerow(review_header)

# Open the file to save the review
if not os.path.exists(all_data_file):
    with open(all_data_file, "w+", encoding="utf-8", newline='') as f:
        csvWriter = csv.writer(f)
        if os.stat(all_data_file).st_size == 0:
            csvWriter.writerow(all_data_header)

def check_exists(name:str):
    try:
        name = name.replace("_", " ")
        results = requests.get(server_sub,
                                params={"q": "*:*",
                                        "fl": "Name",
                                        "rows": "500"}).json()
        res = results.get("response").get("docs")
        for i in res:
            if name == i.get("Name"):
                return True
    except Exception as e:
        logging.error(e)
        pass
    return False

def append_coord(name:str):
    '''
    given a single row in reviews.csv,
    output a new row with coordinates
    appended.
    '''
    address = map_client.geocode(name)
    if address:
        coordinates = address[0]['geometry'].get("location")
        lat = coordinates.get('lat')
        long = coordinates.get('lng')
        return lat, long
    return None


def crawl_single(link: str) -> bool:
    name = link.split("-")[4]
    existence = check_exists(name)
    if existence:
        return False
    print("Getting link...")
    driver = webdriver.Chrome()
    driver.get(link)
    category = ("Hotel" if "Hotel" in link else "Eatery")
    if category == "Eatery":
        completed = crawl_eatery(driver)
    else:
        completed = crawl_hotel(driver)
    driver.close()
    return completed

def crawl_eatery(driver) -> bool:
    category = "Eatery"
    try:
        establishmentType = []
        # get eatery name, eatery type, eatery dietary restrictions
        print("Finding name...")
        name = driver.find_element(By.XPATH, "//h1[@class='HjBfq']").text
        
        # e.g. restaurant, quick bites
        print("Getting Style...")
        establishmentType_1 = [my_elem.text.replace(" in Singapore", "")
                                for my_elem in driver.find_elements(By.XPATH,
                                                                    "//div[@class='cNFlb']/a")]
        establishmentType_2 = [my_elem.text
                                for my_elem in driver.find_elements(By.XPATH,
                                                                    "//span[@class='DsyBj DxyfE']/a")]
        for i in establishmentType_1:
            for k in et:
                if k in i:
                    establishmentType.append(k)

        for i in establishmentType_2:
            for k in et:
                if k in i:
                    establishmentType.append(k)

        establishmentType_noDup = list(dict.fromkeys(establishmentType))            
        print("Getting Style...")
        # e.g. Halal, Vegetarian
        dietaryRestriction_unclean = [my_elem.text
                                        for my_elem in driver.find_elements(By.XPATH,
                                                                            "//div[@class='SrqKb']")]

        dietaryRestriction = []
        for i in dietaryRestriction_unclean:
            for k in dr:
                if k in i:
                    dietaryRestriction.append(k)

        eStyle_list = establishmentType_noDup + dietaryRestriction
        eStyle = '|'.join(eStyle_list)
        print("Getting Star...")
        eStar = driver.find_element(By.XPATH, "//span[@class='ZDEqb']").text
        print("Getting Coordinates...")
        lat, long = append_coord(name)
        with open(all_data_file, 'a', encoding="utf-8", newline='') as f:
            csvWriter = csv.writer(f)
            csvWriter.writerow([name, category, eStyle,
                                eStar, lat, long])
        print("Adding to solr core: all_data...")
        dsolr.add([{
            "Name":name,
            "Category":category,
            "Style":eStyle,
            "Star":eStar,
            "lat":lat,
            "lon":long,
        }])
    except Exception as e:
        logging.error(e)
        pass
    
    # scrap reviews
    # change the value inside the range to save more or less reviews
    for i in range(0, num_page):
        
        time.sleep(2)

        # expand the review 
        try:
            ViewMore = driver.find_element(By.XPATH, "//span[@class='taLnk ulBlueLinks']")
            driver.execute_script("arguments[0].click();", ViewMore)
        except Exception as e:
            logging.error(e)
            continue

        container = driver.find_elements(By.XPATH, ".//div[@class='review-container']")
        print("Adding reviews...")
        for j in range(len(container)):
            
            try:
                title = container[j].find_element(By.XPATH, ".//span[@class='noQuotes']").text
                date = container[j].find_element(By.XPATH, ".//div[@class='prw_rup prw_reviews_stay_date_hsx']").text.replace("Date of visit: ","")
                rating = int(container[j].find_element(By.XPATH, ".//span[contains(@class, 'ui_bubble_rating bubble_')]").get_attribute("class").split("_")[3])/10
                rating = str(rating).rstrip()
                review = container[j].find_element(By.XPATH, ".//p[@class='partial_entry']").text.replace("\n", " ")
                date_obj = datetime.strptime(date, '%B %Y')
                date_formatted = date_obj.strftime('%Y-%m-%d')

                # sentiment
                sentiment = model_predict(review)

                with open(review_file, 'a', encoding="utf-8", newline='') as f:
                    csvWriter = csv.writer(f)
                    csvWriter.writerow([name, category, eStyle,
                                        eStar, date_formatted,
                                        rating, title, review,
                                        sentiment])
                    
                # TODO: add sentiment analysis call function here:
                # input: review
                # TODO: update solr schema for sentiment
                # TODO: flask actions - if page already exists AND if page does not exist
                #                       AND print out the process
                print("Adding to solr core: reviews...")
                rsolr.add([{
                            "Name":name,
                            "Category":category,
                            "Style":eStyle,
                            "Star":eStar,
                            "Date":date_formatted,
                            "Rating":rating,
                            "ReviewTitle":title,
                            "Review":review,
                            # "Sentiment":sentiment,
                        }])
            except Exception as e:
                logging.error(e)
                continue
    return True

def crawl_hotel(driver) -> bool:
    category = "Hotel"
    # get hotel name, hotel class, hotel style
    try:
        print("Adding hotel information...")
        name = driver.find_element(By.XPATH, "//h1[@class='QdLfr b d Pn']").text
        hClass = driver.find_element(By.XPATH, "//*[name()='svg' and @class='JXZuC d H0']").get_attribute("aria-label").split()[0]
        hStyle_all = [my_elem.text for my_elem in driver.find_elements(By.XPATH, "//div[@class='euDRl _R MC S4 _a H']")]
        if "" in hStyle_all:
            hStyle_all.remove("")
        hStyle_list = []
        for x in hStyle_all:
            if "English" not in x:
                hStyle_list.append(x)
        hStyle = '|'.join(hStyle_list)
        lat, long = append_coord(name)
        with open(all_data_file, 'a', encoding="utf-8", newline='') as f:
            csvWriter = csv.writer(f)
            csvWriter.writerow([name, category, hStyle,
                                hClass, lat, long])
        # TODO: sentiment here
        dsolr.add([{
            "Name":name,
            "Category":category,
            "Style":hStyle,
            "Star":hClass,
            "lat":lat,
            "lon":long,
            # "Sentiment":sentiment,
        }])
    except Exception as e:
        logging.error(e)
        pass

    # change the value inside the range to save more or less reviews
    for i in range(0, num_page):

        # expand the review 
        time.sleep(2)
        try:
            driver.find_element(By.XPATH, ".//div[contains(@data-test-target, 'expand-review')]").click()
        except:
            pass

        container = driver.find_elements(By.XPATH, "//div[@class='YibKl MC R2 Gi z Z BB pBbQr']")

        for j in range(len(container)):

            try:
                rating = int(container[j].find_element(By.XPATH, ".//span[contains(@class, 'ui_bubble_rating bubble_')]").get_attribute("class").split("_")[3])/10
                title = container[j].find_element(By.XPATH, ".//div[contains(@data-test-target, 'review-title')]").text
                review = container[j].find_element(By.XPATH, ".//span[@class='QewHA H4 _a']").text.replace("\n", "  ") # site changed to from q to span on 29/3/2023
                date = container[j].find_element(By.XPATH, ".//span[@class='teHYY _R Me S4 H3']").text.replace("Date of stay: ","")
                date_obj = datetime.strptime(date, '%B %Y')
                date_formatted = date_obj.strftime('%Y-%m-%d')

                # sentiment
                sentiment = model_predict(review)
            
                with open(review_file, 'a', encoding="utf-8", newline='') as f:
                    csvWriter = csv.writer(f)
                    csvWriter.writerow([name, category, hStyle,
                                        hClass, date_formatted,
                                        rating, title, review,
                                        sentiment])
            except:
                continue
            
        # change the page            
        if  len(driver.find_elements(By.XPATH, './/a[@class="ui_button nav next primary "]')) > 0:
            NextBtn = driver.find_element(By.XPATH, './/a[@class="ui_button nav next primary "]')
            driver.execute_script("arguments[0].click();", NextBtn)
        else:
            break
    return True