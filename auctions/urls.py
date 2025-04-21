from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("bid/<int:listing_id>", views.bid, name="bid"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("watchlist/<int:listing_id>", views.watchlist, name="watchlist"),
    path("close_listing/<int:listing_id>", views.close_listing, name="close_listing"),
    path("mywatchlist", views.mywatchlist, name="mywatchlist"),
    path("comment/<int:listing_id>", views.comment, name="comment"),
    path("categories", views.categories, name="categories"),
    path("category_listings/<int:category_id>/", views.category_listings, name="category_listings"),
    path("tester", views.tester, name="tester")

]
