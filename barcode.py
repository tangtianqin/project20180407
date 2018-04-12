# coding: UTF-8
# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import jinja2
import sys, os
import webapp2
import json
from datetime import datetime

import logging
import urllib2
from urlparse import urlparse
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
from lxml import html

from BarcodeInfoDB import BarcodeInfoDB
import BarcodeInfo

from google.appengine.api import users
from protorpc import remote

JINJIA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

def AmazonParser(url):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36', 'Accept-Language': 'ja-jp'}
    try:
        page = urlfetch.fetch(url,headers=headers)
        doc = html.fromstring(page.content)
        XPATH_NAME = '//h1[@id="title"]//text()'
        XPATH_SALE_PRICE = '//span[contains(@id,"ourprice") or contains(@id,"saleprice")]/text()'
        XPATH_ORIGINAL_PRICE = '//td[contains(text(),"List Price") or contains(text(),"M.R.P") or contains(text(),"Price")]/following-sibling::td/text()'
        XPATH_CATEGORY = '//a[@class="a-link-normal a-color-tertiary"]//text()'
        XPATH_AVAILABILITY = '//div[@id="availability"]//text()'
        XPATH_BRAND = '//div[@id="bylineInfo_feature_div"]//a[contains(@id, "brand") or contains(@id, "bylineInfo")]//text()'
        XPATH_BOOK_BRAND = '//div[@id="booksTitle"]/div[contains(@id,"byline") or contains(@id, "bylineInfo")]/span/a/text()'

        RAW_NAME = doc.xpath(XPATH_NAME)
        RAW_SALE_PRICE = doc.xpath(XPATH_SALE_PRICE)
        RAW_CATEGORY = doc.xpath(XPATH_CATEGORY)
        RAW_ORIGINAL_PRICE = doc.xpath(XPATH_ORIGINAL_PRICE)
        RAw_AVAILABILITY = doc.xpath(XPATH_AVAILABILITY)
        RAW_BRAND = doc.xpath(XPATH_BRAND)
        #logging.info(RAW_BRAND)
        RAW_BOOK_BRAND = doc.xpath(XPATH_BOOK_BRAND)
        #logging.info(RAW_BOOK_BRAND)

        NAME = ' '.join(''.join(RAW_NAME).split()) if RAW_NAME else None
        #logging.info('Raw price: ' + ''.join(RAW_SALE_PRICE).replace(u'￥', ''))
        SALE_PRICE = ' '.join(''.join(RAW_SALE_PRICE).split()).strip().replace(u'￥', '').replace(',','') if RAW_SALE_PRICE else None
        #logging.info(SALE_PRICE)
        CATEGORY = ' > '.join([i.strip() for i in RAW_CATEGORY]) if RAW_CATEGORY else None
        ORIGINAL_PRICE = ''.join(RAW_ORIGINAL_PRICE).strip().replace(u'￥', '').replace(',', '') if RAW_ORIGINAL_PRICE else None
        AVAILABILITY = ''.join(RAw_AVAILABILITY).strip() if RAw_AVAILABILITY else None
        BRAND = ''.join(RAW_BRAND).strip() if RAW_BRAND else ''.join(RAW_BOOK_BRAND).strip() if RAW_BOOK_BRAND else None

        if not ORIGINAL_PRICE:
            ORIGINAL_PRICE = SALE_PRICE

        if page.status_code!=200:
            logging.info("Status: " + str(page.status_code))
            logging.info(page.content)
            raise ValueError('captha')
        data = BarcodeInfo.BarcodeInfo(
                Name=NAME,
                SalePrice = float(SALE_PRICE) if bool(SALE_PRICE) else -1.0,
                Category = CATEGORY,
                OriginalPrice = float(ORIGINAL_PRICE) if bool(ORIGINAL_PRICE) else -1.0,
                Availability = bool(AVAILABILITY),
                Url = url,
                Brand = BRAND
                )
        # logging.info("Data: " + data)
        return data
    except Exception as e:
        logging.info(e)

def Asin0Parser(url):
    logging.info("Entering Asin0Parser")
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36', 'Accept-Language': 'ja-jp'}
    try:
        page = urlfetch.fetch(url,headers=headers)
        #logging.info("Page: " + page.content)
        doc = html.fromstring(page.content)
        XPATH_NAME = '//div[@id="search-main-wrapper"]//div[@id="atfResults"]//li[@id="result_0"]//a/@href'

        RAW_NAME = doc.xpath(XPATH_NAME)
        if not RAW_NAME:
            logging.info("RAW_NAME is None.")
            return None
        #logging.info("DOM: " + RAW_NAME[0])
        p = urlparse(RAW_NAME[0]) if RAW_NAME else None
        logging.info("url: " + p.path)
        parts = p.path.split('/') if p else None
        i = parts.index("dp") if parts else None
        data = parts[i+1] if i else None
        return data
    except Exception as e:
        logging.info(e)

def ReadBarcode(code):
    # AsinList = csv.DictReader(open(os.path.join(os.path.dirname(__file__),"Asinfeed.csv")))
    extracted_data = []
    url_asin = "https://www.amazon.co.jp/s/ref=nb_sb_noss?field-keywords="+code
    logging.info("Processing: "+url_asin)
    asin = Asin0Parser(url_asin)
    logging.info(asin)
    if asin:
        url = "https://www.amazon.co.jp/dp/"+asin
        info = AmazonParser(url)
        if info: 
            info.Asin = asin
            info.Barcode = code
        return info

class MainPage(webapp2.RequestHandler):
    def get(self):
        code = self.request.GET['code']
        info = ReadBarcode(code) if code and len(code) == 13 else None
        if not info:
            self.response.status_message = 'No information about '
            self.response.set_status(404)
        else:
            data = remote.protojson.encode_message(info)
            self.response.content_type='application/json'
            self.response.out.write(data)
        
    def post(self):
        try:
            info = remote.protojson.decode_message(BarcodeInfo.BarcodeInfo, self.request.body)
            infoDB = BarcodeInfoDB.findByBarcode(info.Barcode)
            if infoDB:
                self.response.set_status(200)
                self.response.out.write("")
            else: 
                #logging.info(info.NAME)
                infoDB = BarcodeInfoDB.from_dict(json.loads(self.request.body))
                infoDB.CreatedDate = datetime.now()
                logging.info(infoDB)
                infoDB.put()
                self.response.out.write(infoDB.key)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            logging.info(e)
            self.response.set_status(400)
app = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)

