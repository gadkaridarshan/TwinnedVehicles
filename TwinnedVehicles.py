#=============================================================================
# Class Database
# Latest Update Date: Oct 3, 2018
# Author: Darshan Gadkari
#
#
#
#=============================================================================

# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup

import pandas as pd
import numpy as np

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

import logging
LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -15s %(funcName) '
              '-15s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)

class TwinnedVehicles:
    def __init__(self):
        """
        Constructor
        """
        # Setup headless Firefox browser
        options = Options()
        options.add_argument("--headless")
        self.browser = webdriver.Firefox(firefox_options=options, executable_path='./geckodriver')
    
    def execute(self):
        """
        Execute method
        """
        try:
            # Setup headless Firefox browser
            options = Options()
            options.add_argument("--headless")
            self.browser = webdriver.Firefox(firefox_options=options, executable_path='./geckodriver')
            # Browse to google
            gameURL = 'https://google.com'
            self.browser.get(gameURL)
            # Enter the text to search
            tbox = self.browser.find_element_by_id("lst-ib")
            tbox.send_keys("twinned vehicles")
            logo = self.browser.find_element_by_id("hplogo").click()
            
            self.browser.find_element_by_name("btnK").click()

            # Beautiful Soup
            soup = BeautifulSoup(self.browser.page_source, 'html.parser')
            divs = soup.findAll("div", {"class": "rc"})
            if len(divs) == 0:
                divs = soup.findAll("div", {"class": "r"})

            # List of manufacturers and cars needs to be extracted from some database or repository
            # This is key to the success of the scraper
            manufacturers = ['chevrolet','buick','gmc','vauxhall','opel','audi','vw','volkswagen','porsche','bmw','ford',\
                'lincoln','toyota','lexus','cadillac','dodge','chrysler','pontiac','jeep','kia','saturn',\
                'nissan','infiniti']
            cars = ['corvette','xlr','enclave','acadia','equinox','aura','torrent','yukon','escalade','h2','lacrosse',\
                   'traverse','outlook','durango','aspen','compass','patriot','malibu','g6','impala','avenger','armada',\
                    'qx56','sportage','tuscon','g','ix','ls','370z']

            # Google obviously returns a list of results. We will only scrape from result site 1
            # Every site will need a different scraping strategy
            for div in divs[:1]:
                hrefs = div.findAll("a")
                for href in hrefs[:1]:
                    self.browser.get(href.get("href"))

                    soup1 = BeautifulSoup(self.browser.page_source, 'html.parser')

                    matches = []

                    carItems = soup1.findAll('a')
                    # for other sites it could h2 or h3 or div instead of a

                    for carItem in carItems:
                        for manufacturer in manufacturers:
                            othermanus = [n for n in manufacturers if n != manufacturer]
                            carI = carItem.text.lower().replace('/',' ').replace('\n',' ')
                            carP = carItem.parent.text.lower().replace('/',' ').replace('\n',' ')
                            if manufacturer in carI:
                                for othermanu in othermanus:
                                    if othermanu in carP:
                                        for car in cars:
                                            if car in carP:
                                                matches.append([carP.split(car)[0].strip().split(' ')[-1]\
                                                      .split('/')[-1],car,othermanu,carP.split(othermanu)[1].\
                                                      strip().split(' ')[0].split('/')[-1]])


                    # Convert matches which is a list of lists into the Pandas DataFrame
                    pdM = pd.DataFrame(matches)
                    pdM = pdM.rename(columns={0:'Manu1',1:'Car1',2:'Manu2',3:'Car2'})
                    pdM = pdM[(pdM['Car2'].notnull()) & (pdM['Car2'] != '')]
                    pdM = pdM[(pdM['Car1'].notnull()) & (pdM['Car1'] != '')]
                    pdM = pdM[pdM['Car1'].isin(cars)]
                    pdM = pdM[pdM['Car2'].isin(cars)]

                    pdM.drop_duplicates(['Manu2','Car2'],keep='first',inplace=True)
                    pdM.drop_duplicates(['Manu1','Car1'],keep='first',inplace=True)

                    pdM = pdM[(pdM['Car1'] != pdM['Car2'])]

                    pdMSM = pdM[pdM['Manu1'] == pdM['Manu2']]
                    print(pdMSM.shape)
                    print(pdMSM)
                    LOGGER.info("=== Same manufacturer different car")
                    LOGGER.info(pdMSM)

                    pdMDM = pdM[pdM['Manu1'] != pdM['Manu2']]
                    print(pdMDM.shape)
                    print(pdMDM)
                    LOGGER.info("=== different manufacturers")
                    LOGGER.info(pdMDM)

                    pdMSM['Manu1-Car1'] = pdMSM['Manu1'] + ' ' + pdMSM['Car1']
                    pdMSM['Manu2-Car2'] = pdMSM['Manu2'] + ' ' + pdMSM['Car2']
                    pdMDM['Manu1-Car1'] = pdMDM['Manu1'] + ' ' + pdMDM['Car1']
                    pdMDM['Manu2-Car2'] = pdMDM['Manu2'] + ' ' + pdMDM['Car2']

                    pdMSM.apply(self.getListOfImages,column='Manu1-Car1',axis=1)
                    pdMSM.apply(self.getListOfImages,column='Manu2-Car2',axis=1)
                    pdMDM.apply(self.getListOfImages,column='Manu1-Car1',axis=1)
                    pdMDM.apply(self.getListOfImages,column='Manu2-Car2',axis=1)

        except Exception as e:
            LOGGER.critical(e)

    def getListOfImages(self,row,column):
        try:
            gameURL = 'https://google.com'
            self.browser.get(gameURL)
            tbox = self.browser.find_element_by_id("lst-ib")
            tbox.send_keys(row[column])

            logo = self.browser.find_element_by_id("hplogo").click()
            logo = self.browser.find_element_by_id("hplogo").click()
            logo = self.browser.find_element_by_id("hplogo").click()

            self.browser.find_element_by_name("btnK").click()
            
            images = self.browser.find_element_by_link_text("Images").click()
            s = BeautifulSoup(self.browser.page_source, 'html.parser')
            divs = s.findAll("a", {"class": "rg_l"})
            
            outputList = []
            for div in divs:
                if div.findAll("img")[0].get('data-src'):
                    outputList.append(div.findAll("img")[0].get('data-src'))
            LOGGER.info(len(outputList))
            np.savetxt(row[column] + ".csv", outputList, delimiter=",", fmt='%s', header='Images')

        except Exception as e:
            LOGGER.critical(e)

if __name__ == "__main__":
    tv = TwinnedVehicles()
    tv.execute()