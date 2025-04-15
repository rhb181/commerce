from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField(max_length=240)
    starting_bid = models.DecimalField(max_digits=5, decimal_places=2)
    image_url = models.CharField(max_length=1000)
    isActive = models.BooleanField(default=True)
    listed_by = models.ForeignKey(User,on_delete=models.CASCADE, related_name="user")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True, related_name="category")
    