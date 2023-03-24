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

# default tripadvisor website of hotel

with open('links_hotels.csv', 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        url = row[0]
# if you pass the inputs in the command line
        if (len(sys.argv) == 4):
            path_to_file = sys.argv[1]
            num_page = int(sys.argv[2])
            url = sys.argv[3]

        # import the webdriver
        driver = webdriver.Chrome()
        driver.get(url)

        # get hotel name, hotel class, hotel style
        try:
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
        except:
            continue

        # open the file to save the review
        csvFile = open(path_to_file, 'a', encoding="utf-8", newline='')
        csvWriter = csv.writer(csvFile)
        # csvWriter.writerow(["Name","Category","Style","Star","Date", "Rating", "ReviewTitle", "Review"]) 

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
                    review = container[j].find_element(By.XPATH, ".//q[@class='QewHA H4 _a']").text.replace("\n", "  ")
                    date = container[j].find_element(By.XPATH, ".//span[@class='teHYY _R Me S4 H3']").text.replace("Date of stay: ","")
                
                    csvWriter.writerow([name, "Hotel", hStyle, hClass, date, rating, title, review]) 
                except:
                    continue
                
            # change the page            
            if  len(driver.find_elements(By.XPATH, './/a[@class="ui_button nav next primary "]')) > 0:
                NextBtn = driver.find_element(By.XPATH, './/a[@class="ui_button nav next primary "]')
                driver.execute_script("arguments[0].click();", NextBtn)
            else:
                break

        driver.quit()