from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_list_or_404, get_object_or_404
from django.contrib import messages
from django.db.models import Max 


from .models import User, Listing, Category, Bid, Comment


def index(request):
    listings = Listing.objects.filter(isActive=True)
    return render(request, "auctions/index.html", {
        "listings": listings
    })
    
def listing(request, listing_id):
    try:
        listing = Listing.objects.get(id=listing_id)
    except Listing.DoesNotExist:
        return HttpResponse("Listing not found.", status=404)

    comments = listing.comments.filter(listing_id=listing_id)

    in_watchlist = listing.watchlist.filter(id=request.user.id).exists()
    
    bid_count = Bid.objects.filter(listing=listing).count()
    
    bids = Bid.objects.filter(listing=listing)
    if bids.exists():
        highest_bid = bids.order_by('-amount').first()
        highest_bid_amount = highest_bid.amount
        highest_bidder = highest_bid.bidder 
    else:
        highest_bid_amount = listing.starting_bid
        highest_bidder = None
    
    is_highest_bidder = False
    if request.user.is_authenticated and highest_bidder == request.user:
        is_highest_bidder = True
                
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "in_watchlist": in_watchlist,
        "highest_bid_amount": highest_bid_amount,        
        "bid_count": bid_count,
        "higher_bidder": highest_bidder,
        "is_highest_bidder": is_highest_bidder,
        "comments": comments
        
    })
        

@login_required(login_url="login") 
def close_listing(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)
    
    if request.user != listing.listed_by:
        messages.error(request, "You are not authorized to close this listing.")
        return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
    
    bids = Bid.objects.filter(listing=listing)
    if bids.exists():
        highest_bid = bids.order_by('-amount').first()
        listing.winner = highest_bid.bidder 
        
    listing.isActive = False
    listing.is_closed = True
    listing.save()
    
    messages.success(request, "The listing has been closed.", extra_tags="success_2")
    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
    

@login_required(login_url="login")
def bid(request, listing_id):
    
    listing = Listing.objects.get(id=listing_id)
    owner = listing.listed_by
    bidder = request.user
    starting_bid = listing.starting_bid
    bids = Bid.objects.filter(listing=listing)
    this_bid = float(request.POST.get("bid_value"))
    
    if owner == bidder:
        messages.error(request, f"You cannot place a bid, you are the listing owner", extra_tags="error_1")
        return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
        
    if bids.exists():
        highest_bid = bids.order_by('-amount').first().amount  # Get the highest bid amount
    else:
        highest_bid = starting_bid

    if highest_bid < this_bid:            
        b = Bid(listing = listing,
                bidder = bidder,
                amount = this_bid)
        b.save()
        messages.success(request, f"Your bid of ${this_bid:.2f} was successfully placed!", extra_tags="success_1")
    else:
        messages.error(request, f"Sorry..your bid must be higher than the current highest bid of ${highest_bid:.2f}.", extra_tags="error_2")
    
    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))


@login_required(login_url="login")
def mywatchlist(request):
    watchlist_items = Listing.objects.filter(watchlist=request.user).annotate(highest_bid=Max('bids__amount')).order_by('-isActive','-id')

    return render(request, "auctions/mywatchlist.html", {
        "listings": watchlist_items
    })
    
@login_required(login_url="login")
def watchlist(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)
    
    user = request.user

    if user in listing.watchlist.all():
        listing.watchlist.remove(user)
    else:
        listing.watchlist.add(user)

    print("After:", listing.watchlist.all())  # 

    return HttpResponseRedirect(reverse("listing", args=(listing.id,)))


@login_required(login_url="login")
def create(request):
    if request.method == "POST":
        try:
            category_id = request.POST.get("category")
            category = get_object_or_404(Category, id=category_id) if category_id else None
            
            l = Listing(title = request.POST["title"], 
                        description = request.POST["description"],
                        starting_bid = request.POST["starting_bid"],
                        image_url = request.POST["image_url"],
                        isActive = "is_active" in request.POST,
                        listed_by = request.user,
                        category = category)
            l.save()
            return HttpResponseRedirect(reverse("index"))
        except Exception as e:
            print("Error:", e)
            return HttpResponseBadRequest("Invalid data submitted.")
    
    elif request.method == "GET":
        categories = Category.objects.all()
        users = User.objects.all()
        return render(request, "auctions/create.html", {
            "categories": categories,
            "current_user": request.user 
        })

def comment(request, listing_id):
    if request.method == "POST":
        listing = get_object_or_404(Listing, id=listing_id)
        comment_text = request.POST.get("comment")
        comment_by = request.user
        
        print("Listing:", listing)
        print("Comment Text:", comment_text)
        print("Comment By:", comment_by)
        
        if not comment_text.strip():
            print("Empty comment submitted.")
            return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
        
        try:
            c = Comment(comment = comment_text, 
                        comment_by = comment_by,
                        listing = listing)
            c.save()
            print("Comment saved successfully.")

            return HttpResponseRedirect(reverse("comment", args=(listing_id,)))
        except Exception as e:
            print("Error:", e)
            return HttpResponseRedirect(reverse("comment", args=(listing_id,)))  
    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
  
def categories(request):
        categories = Category.objects.all()
        return render(request, "auctions/categories.html", {
            "categories": categories
        })
        
def tester(request):
    return render(request, "auctions/tester.html")
        
def category_listings(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    listings = Listing.objects.filter(category=category, isActive=True)

    return render(request, "auctions/category_listings.html", {
        "category": category,
        "listings": listings
    })
        
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
