from django.db import models
from multiselectfield import MultiSelectField
# Create your models here.
# from django.core.files.storage import DEFAULT_FILE_STORAGE

class Matching(models.Model):
    name = models.CharField(max_length = 100)
    sell_topics = models.CharField(max_length = 100)
    buy_topics = models.CharField(max_length = 100)
    city = models.CharField(max_length = 100)
    study_topics = models.CharField(max_length = 100)
    email = models.EmailField(max_length = 254, default = 'None')
    sell_price = models.DecimalField(decimal_places = 2, max_digits=100, default=10.00)

    #books to sell, books to buy, topics to study together, location of residence

class Comment(models.Model):
    identifier = models.CharField(max_length = 500, default = "")
    comment = models.CharField(max_length = 500)
    impact = models.DecimalField(decimal_places = 0, max_digits=100)
    
