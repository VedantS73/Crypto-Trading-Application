from django.urls import path, reverse_lazy
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    path("", RedirectView.as_view(url=reverse_lazy('screener'), permanent=False), name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("screener",views.screener, name="screener"),
    path("coin/<str:id>", views.coin, name="coin"),
    path("buy/<str:coin_id>",views.buy, name="buy"),
    path("cash", views.cash, name="cash"),
    path("holdings",views.holdings,name="holdings"),
    path("sell/<str:id>/<str:price>/<str:qty>", views.sell, name="sell"),
    path("all/<int:page>", views.all, name="all"),
    path("deposit", views.deposit, name="deposit"),
    path("withdraw", views.withdraw, name="withdraw"),
    path("coincall/<str:coinid>",views.coincall,name="coincall"),
]