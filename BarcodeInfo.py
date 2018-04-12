# coding: UTF-8

from protorpc import messages
from protorpc import message_types

class BarcodeInfo(messages.Message):
    """A proto Message that contains a simple string field."""
    Name = messages.StringField(1)
    SalePrice = messages.FloatField(2, default=0.0)
    Category = messages.StringField(3, default="")
    OriginalPrice = messages.FloatField(4, default=0.0)
    Availability = messages.BooleanField(5, default=False)
    Url = messages.StringField(6, default="")
    Brand = messages.StringField(7, default="")
    Barcode = messages.StringField(8, default="")
    Asin = messages.StringField(9, default="")
    CreatedDate = message_types.DateTimeField(10)
    Longitude = messages.FloatField(11, default=0.0)
    Latitude = messages.FloatField(12, default=0.0)
