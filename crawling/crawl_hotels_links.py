import sys
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os

# default path to file to store data
path_to_file = os.getcwd() + "\\crawling\\links_hotels.csv"

# default number of scraped pages
num_page = 1

# default tripadvisor website of hotel
url = "https://www.tripadvisor.com/Hotels-g294265-zft21371-Singapore-Hotels.html"

# if you pass the inputs in the command line
if (len(sys.argv) == 4):
    path_to_file = sys.argv[1]
    num_page = int(sys.argv[2])
    url = sys.argv[3]

# import the webdriver
driver = webdriver.Chrome()
driver.get(url)

# open the file to save the review
csvFile = open(path_to_file, 'a', encoding="utf-8", newline='')
csvWriter = csv.writer(csvFile)

# change the value inside the range to save more or less reviews
for i in range(0, num_page): 

    time.sleep(2)
    container = driver.find_elements(By.XPATH, "//div[@class='prw_rup prw_meta_hsx_responsive_listing ui_section listItem reducedWidth rounded']")

    for j in range(len(container)):

        try:
            # dataUrl = container[j].find_element(By.XPATH, ".//div[@class='listing_title ']/a").get_attribute("href")
            if(container[j].find_element(By.XPATH, ".//a[@class='review_count']").text != "0 reviews"):
                dataUrl = container[j].find_element(By.XPATH, ".//div[@class=' photo-wrapper  roundedCell']/a").get_attribute("href")
                csvWriter.writerow([dataUrl]) 
        except:
            pass
    
        
    # change the page            
    if  len(driver.find_elements(By.XPATH, './/a[@class="nav next ui_button primary"]')) > 0:
        NextBtn = driver.find_element(By.XPATH, './/a[@class="nav next ui_button primary"]')
        driver.execute_script("arguments[0].click();", NextBtn)
    else:
        break

driver.quit()
