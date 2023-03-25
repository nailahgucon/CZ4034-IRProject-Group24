import sys
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os

# default path to file to store data
path_to_file = os.getcwd() + "\\reviews_combined.csv"

# default number of scraped pages
num_page = 1

with open('crawling\\links_eateries.csv', 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        url = row[0]
        # if you pass the inputs in the command line
        if (len(sys.argv) == 4):
            path_to_file = sys.argv[1]
            num_page = int(sys.argv[2])
            url = sys.argv[3]

        # Import the webdriver
        driver = webdriver.Chrome()
        driver.get(url)

        try: 
            # get eatery name, eatery type, eatery dietary restrictions
            name = driver.find_element(By.XPATH, "//h1[@class='HjBfq']").text
            # e.g. restaurant, quick bites
            establishmentType_1 = [my_elem.text.replace(" in Singapore", "") for my_elem in driver.find_elements(By.XPATH, "//div[@class='cNFlb']/a")]

            establishmentType_2 = [my_elem.text for my_elem in driver.find_elements(By.XPATH, "//span[@class='DsyBj DxyfE']/a")]

            et = ["Restaurants", "Fast Food", "Quick Bites","Dessert","Coffee & Tea","Bakeries","Bars & Pubs","Specialty Food Market","Delivery Only"]

            establishmentType = []

            for i in establishmentType_1:
                for k in et:
                    if k in i:
                        establishmentType.append(k)

            for i in establishmentType_2:
                for k in et:
                    if k in i:
                        establishmentType.append(k)

            establishmentType_noDup = list(dict.fromkeys(establishmentType))            

            # e.g. Halal, Vegetarian
            dietaryRestriction_unclean = [my_elem.text for my_elem in driver.find_elements(By.XPATH, "//div[@class='SrqKb']")]

            dr = ["Halal", "Vegetarian Friendly", "Vegan Options", "Kosher", "Gluten Free Options"]

            dietaryRestriction = []

            for i in dietaryRestriction_unclean:
                for k in dr:
                    if k in i:
                        dietaryRestriction.append(k)

            eStyle_list = establishmentType_noDup + dietaryRestriction
            eStyle = '|'.join(eStyle_list)

            eStar = driver.find_element(By.XPATH, "//span[@class='ZDEqb']").text
        except:
            continue


        # Open the file to save the review
        csvFile = open(path_to_file, 'a', encoding="utf-8", newline='')
        csvWriter = csv.writer(csvFile)
        # csvWriter.writerow(["Name","Category","Style","Star","Date", "Rating", "ReviewTitle", "Review"]) 

        # change the value inside the range to save more or less reviews
        for i in range(0, num_page):
            
            time.sleep(2)

            # expand the review 
            try:
                ViewMore = driver.find_element(By.XPATH, "//span[@class='taLnk ulBlueLinks']")
                driver.execute_script("arguments[0].click();", ViewMore)
            except:
                continue

            container = driver.find_elements(By.XPATH, ".//div[@class='review-container']")

            for j in range(len(container)):
                
                try:
                    title = container[j].find_element(By.XPATH, ".//span[@class='noQuotes']").text
                    date = container[j].find_element(By.XPATH, ".//div[@class='prw_rup prw_reviews_stay_date_hsx']").text.replace("Date of visit: ","")
                    rating = int(container[j].find_element(By.XPATH, ".//span[contains(@class, 'ui_bubble_rating bubble_')]").get_attribute("class").split("_")[3])/10
                    review = container[j].find_element(By.XPATH, ".//p[@class='partial_entry']").text.replace("\n", " ")

                    csvWriter.writerow([name, "Eatery", eStyle, eStar, date, rating, title, review]) 
                except:
                    continue
            
            # change the page     
            if  len(driver.find_elements(By.XPATH, './/a[@class="nav next ui_button primary"]')) > 0:
                NextBtn = driver.find_element(By.XPATH, './/a[@class="nav next ui_button primary"]')
                driver.execute_script("arguments[0].click();", NextBtn)
            else:
                break

        driver.close()
