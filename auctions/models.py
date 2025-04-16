from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length=64)
    
    def __str__(self):
        return self.name

class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField(max_length=240)
    starting_bid = models.DecimalField(max_digits=8, decimal_places=2)
    image_url = models.CharField(max_length=1000)
    isActive = models.BooleanField(default=True)
    listed_by = models.ForeignKey(User,on_delete=models.CASCADE, related_name="listings")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True, related_name="category")
    
    def __str__(self):
        return self.title
    
class Watchlist(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="watchlist")
    watcher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist")

class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")  # Unique related_name
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bidder.username} bid {self.amount} on {self.listing.title}"
    
    
class Comment(models.Model):
    comment = models.TextField(max_length=240)
    comment_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments" )
    timestamp = models.DateTimeField(auto_now_add=True)
    