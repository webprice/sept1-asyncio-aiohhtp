from django.db import models
from django.contrib.auth.models import User

#

class Data(models.Model):
    title = models.CharField(max_length=200,null=True)
    price = models.CharField(max_length=200,null=True)
    photo = models.CharField(max_length=200,null=True)
    seller = models.CharField(max_length=200,null=True)
