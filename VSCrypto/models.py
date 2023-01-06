from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class User(AbstractUser):
    balance = models.FloatField(default=0)

class Coin(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="usercoin")
    coinid = models.CharField(max_length=25)
    buyprice = models.FloatField(default=0)
    quantity = models.FloatField(default=0)