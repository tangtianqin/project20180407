# coding: utf-8
# Copyright 2016 Google Inc. All rights reserved.
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

"""This is a sample Hello World API implemented using Google Cloud
Endpoints."""

# [START imports]
import logging
import endpoints
import urllib2
from urlparse import urlparse
from google.appengine.api import urlfetch
from protorpc import message_types
from protorpc import messages
from protorpc import remote
from lxml import html

# [END imports]


# [START messages]
class EchoRequest(messages.Message):
    content = messages.StringField(1)


class EchoResponse(messages.Message):
    """A proto Message that contains a simple string field."""
    NAME = messages.StringField(1)
    SALE_PRICE = messages.FloatField(2, default=0.0)
    CATEGORY = messages.StringField(3, default="")
    ORIGINAL_PRICE = messages.FloatField(4, default=0.0)
    AVAILABILITY = messages.BooleanField(5, default=False)
    URL = messages.StringField(6, default="")
    BRAND = messages.StringField(7, default="")

ECHO_RESOURCE = endpoints.ResourceContainer(
    EchoRequest,
    n=messages.IntegerField(2, default=1))
# [END messages]

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
            raise ValueError('captha')
        data = EchoResponse(
                NAME=NAME,
                SALE_PRICE = float(SALE_PRICE) if bool(SALE_PRICE) else -1.0,
                CATEGORY = CATEGORY,
                ORIGINAL_PRICE = float(ORIGINAL_PRICE) if bool(ORIGINAL_PRICE) else -1.0,
                AVAILABILITY = bool(AVAILABILITY),
                URL = url,
                BRAND = BRAND
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
        #logging.info("DOM: " + RAW_NAME[0])
        p = urlparse(RAW_NAME[0]) if RAW_NAME else None
        logging.info("url: " + p.path)
        parts = p.path.split('/') if p else None
        i = parts.index("dp") if parts else None
        data = parts[i+1] if i else None
        return data
    except Exception as e:
        logging.info(e)

def ReadBarcode(listCode):
    # AsinList = csv.DictReader(open(os.path.join(os.path.dirname(__file__),"Asinfeed.csv")))
    extracted_data = []
    url_asin = "https://www.amazon.co.jp/s/ref=nb_sb_noss?field-keywords="+listCode
    logging.info("Processing: "+url_asin)
    asin = Asin0Parser(url_asin)
    logging.info(asin)
    if asin:
        url = "https://www.amazon.co.jp/dp/"+asin
        return AmazonParser(url)

# [START echo_api]
@endpoints.api(name='echo', version='v1')
class EchoApi(remote.Service):

    @endpoints.method(
        # This method takes a ResourceContainer defined above.
        ECHO_RESOURCE,
        # This method returns an Echo message.
        EchoResponse,
        path='echo',
        http_method='POST',
        name='echo')
    def echo(self, request):
        # output_content = ';'.join([request.content] * request.n)
        output_content = ReadBarcode(request.content.strip())
        logging.info(output_content)
        return output_content

    @endpoints.method(
        # This method takes a ResourceContainer defined above.
        ECHO_RESOURCE,
        # This method returns an Echo message.
        EchoResponse,
        path='echo/{n}',
        http_method='POST',
        name='echo_path_parameter')
    def echo_path_parameter(self, request):
        output_content = ' '.join([request.content] * request.n)
        return EchoResponse(NAME=output_content)

    @endpoints.method(
        # This method takes a ResourceContainer defined above.
        message_types.VoidMessage,
        # This method returns an Echo message.
        EchoResponse,
        path='echo/getApiKey',
        http_method='GET',
        name='echo_api_key')
    def echo_api_key(self, request):
        return EchoResponse(NAME=request.get_unrecognized_field_info('key'))

    @endpoints.method(
        # This method takes an empty request body.
        message_types.VoidMessage,
        # This method returns an Echo message.
        EchoResponse,
        path='echo/getUserEmail',
        http_method='GET',
        # Require auth tokens to have the following scopes to access this API.
        scopes=[endpoints.EMAIL_SCOPE],
        # OAuth2 audiences allowed in incoming tokens.
        audiences=['your-oauth-client-id.com'])
    def get_user_email(self, request):
        user = endpoints.get_current_user()
        # If there's no user defined, the request was unauthenticated, so we
        # raise 401 Unauthorized.
        if not user:
            raise endpoints.UnauthorizedException
        return EchoResponse(NAME=user.email())
# [END echo_api]


# [START api_server]
api = endpoints.api_server([EchoApi])
# [END api_server]
