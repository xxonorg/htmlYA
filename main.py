# iunno lol


import requests
import json
from html import unescape
from config import *
import re
from bs4 import BeautifulSoup

class Restaurant:

    def __init__(self, name, devName):
        self.name = name
        self.devName = devName

    def __repr__(self):
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
        # Deprecated regex # restaurants = re.findall(r'(?<=title=\")(.*)(?=\" class="arrivalLogo\">)', unescapedResponse)
        soup = BeautifulSoup(unescapedResponse, "lxml")
        restaurants = []
        for i in soup.find_all('a', {'class':'arrivalLogo'}):
            restaurantObject = Restaurant(i.string, i.get('href').split('/')[-1])
            restaurants.append(restaurantObject)
            print(type(restaurantObject))
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



initiator = peyaSearch(location, address, country)
print(initiator.get(storeType="COFFEE"))
# initiator.getNextPage()
# initiator.getPrevPage()