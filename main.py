# iunno lol


import requests
import json
from html import unescape
from config import *
import re
from bs4 import BeautifulSoup

class Restaurant:

    def __getPage(self):
        response = requests.get(f'https://www.pedidosya.com.ar/restaurantes/{self.location}/{self.devName}',
                     headers={"Accept": "*/*",
                              "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
                              "Accept-Encoding": "gzip, deflate", "Accept-Language": "en-US,en;q=0.9"})
        self.restaurantPage = response.text

    def __init__(self, name, devName, location):
        self.name = name
        self.devName = devName
        self.location = location

        # self.restaurantPage = self.__getPage()

    def getDetails(self):
        # response = requests.get(f'https://www.pedidosya.com.ar/restaurantes/{self.location}/{self.devName}',
        #              headers={"Accept": "*/*",
        #                       "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
        #                       "Accept-Encoding": "gzip, deflate", "Accept-Language": "en-US,en;q=0.9"})
        # self.restaurantPage = response.text
        try:
            soup = BeautifulSoup(self.restaurantPage, 'lxml')
            dates = soup.findAll('div', attrs={'itemprop': 'openingHoursSpecification'})

            allTimes = {}
            for date in dates:
                # print(date.findAll('span'))
                timesOpen = date.findAll('span', attrs={'itemprop': 'opens'})
                timeClosed = date.findAll('span', attrs={'itemprop': 'closes'})
                day = date.find('div').text
                times = []
                for index, openTime in enumerate(timesOpen):
                    parsedTimeString = ''
                    parsedTimeString += f"{openTime.text}-{timeClosed[index].text}"
                    times.append(parsedTimeString)

                allTimes[day] = times
            self.openTimes = allTimes

            self.address = soup.find('span', attrs={'itemprop': 'streetAddress'}).text

            # print(self.openTimes)
            # print(self.address)
            return self.openTimes, self.address
        except AttributeError:
            self.__getPage()
            self.getDetails()

    def getProductDetails(self):
        try:
            # <li class="peyaCard product-full-card product " data-id="number" data-options="" data-autolink="combo-whopper&reg;" data-auto="shopdetails_product" data-agecheck="false" data-quantity="">
            soup = BeautifulSoup(self.restaurantPage, 'lxml')
            productIdList = soup.findAll('li', attrs={'class':'peyaCard product-full-card product'})
        except AttributeError:
            self.__getPage()
            self.getProductDetails()


    def __repr__(self):
        return self.name
    def __str__(self):
        return self.name

class peyaSearch:

    def __init__(self, location, address, country, delivery_by_peya=None, category=None):

        self.country = country
        self.location = location
        self.address = address
        self.delivery_by_peya = delivery_by_peya
        self.category = category
        self.MaxValues = {"RESTAURANT": None,
                          "GROCERIES": None,
                          "DRINKS": None,
                          "KIOSKS": None,
                          "COFFEE": None,
                          "SHOP": None,
                          "PETS": None}

    def __getCoordinates(self):
        response = requests.get(f"https://www.pedidosya.com.ar/searchBar/getCoordinatesByAddress?&country={self.country}&city={self.location}&address={self.address}",
                     headers = {"Accept": "*/*","User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36","Accept-Encoding": "gzip, deflate","Accept-Language": "en-US,en;q=0.9"})
        # print(response.text)
        # self.address = json.loads(response.text)["data"]["addresses"][0]["street"]
        self.address_number = json.loads(response.text)["data"]["addresses"][0]["door"]
        self.long = json.loads(response.text)["data"]["addresses"][0]["lng"]
        self.lat = json.loads(response.text)["data"]["addresses"][0]["lat"]

    def __getRestaurantNames(self, unescapedResponse):
        #Regex for now, i'll change it to LXML later...
        restaurants = re.findall(r'(?<=title=\")(.*)(?=\" class="arrivalLogo\">)', unescapedResponse)
        soup = BeautifulSoup(unescapedResponse, "lxml")
        restaurants = []
        for i in soup.find_all('a', {'class':'arrivalLogo'}):
            # print(i)
            restaurantObject = Restaurant(name=i.get('title'), devName=i.get('href').split('/')[-1], location=self.location)
            restaurants.append(restaurantObject)
            # print(restaurantObject)
        # print(restaurants)
        return restaurants


    def __getMaxLoop(self, htmlResponse):
        maxLoop = re.findall(r'&amp;page=(\d\d)">\d\d</a></li>\n<li class="arrow next">', htmlResponse)
        return maxLoop

    def get(self, pageNum=1, storeType="RESTAURANT"):
        self.__getCoordinates()
        response = requests.get(f"https://www.pedidosya.com.ar/restaurantes/{self.location}?a={self.address}&doorNumber={2465}&lat={str(self.lat)}&lng={str(self.long)}&page={pageNum}&bt={storeType}",
                                headers={"Upgrade-Insecure-Requests": "1","User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9","Sec-Fetch-Site": "same-origin","Referer": "https://www.pedidosya.com.ar","Sec-Fetch-Mode": "navigate","Sec-Fetch-User": "?1","Sec-Fetch-Dest": "document","Accept-Encoding": "gzip, deflate","Accept-Language": "en-US,en;q=0.9"})
        # print(unescape(response.text))
        self.currentPage = unescape(response.text)
        self.currentPageNum = pageNum
        restaurantNames = self.__getRestaurantNames(self.currentPage)

        return restaurantNames