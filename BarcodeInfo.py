# coding: UTF-8

from protorpc import messages
from protorpc import message_types

class BarcodeInfo(messages.Message):
    """A proto Message that contains a simple string field."""
    NAME = messages.StringField(1)
    SALE_PRICE = messages.FloatField(2, default=0.0)
    CATEGORY = messages.StringField(3, default="")
    ORIGINAL_PRICE = messages.FloatField(4, default=0.0)
    AVAILABILITY = messages.BooleanField(5, default=False)
    URL = messages.StringField(6, default="")
    BRAND = messages.StringField(7, default="")
    Barcode = messages.StringField(8, default="")
    Asin = messages.StringField(9, default="")
    ImportTime = message_types.DateTimeField(10)
