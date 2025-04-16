from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import User, Listing, Category, Bid


def index(request):
    return render(request, "auctions/index.html")

@login_required(login_url="login")
def create(request):
    if request.method == "POST":
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
    
    elif request.method == "GET":
        categories = Category.objects.all()
        users = User.objects.all()
        return render(request, "auctions/create.html", {
            "categories": categories,
            "current_user": request.user 
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
