# coding: UTF-8

from google.appengine.ext import ndb
import datetime

class BarcodeInfoDB(ndb.Expando):
    Name = ndb.StringProperty()
    SalePrice = ndb.FloatProperty()
    Category = ndb.StringProperty()
    OriginalPrice = ndb.FloatProperty()
    Availability = ndb.BooleanProperty()
    Url = ndb.StringProperty()
    Brand = ndb.StringProperty()
    Barcode = ndb.StringProperty()
    Asin = ndb.StringProperty()
    CreatedDate = ndb.DateTimeProperty()
    Longitude = ndb.FloatProperty()
    Latitude = ndb.FloatProperty()

    @classmethod
    def from_dict(cls, d):
        excluded = ('key', 'id')
        df = {k:v for k,v in d.iteritems() if k not in excluded}
        result = cls(**df)
        if 'id' in d:
            result.key = ndb.Key('BarcodeInfoDB', long(d['id']))
        return result

    @classmethod
    def findByBarcode(cls, code):
        return cls.query(cls.Barcode == code).fetch()
