import json
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
import requests
from django.shortcuts import render

from VSCrypto.models import User, Coin

# Create your views here.


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
            return render(request, "VSCrypto/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "VSCrypto/login.html")

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
            return render(request, "VSCrypto/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "VSCrypto/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("screener"))
    else:
        return render(request, "VSCrypto/register.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("screener"))

def dashboard(request):
    return render(request, "VSCrypto/dashboard.html")

def screener(request):
    try:
        coindata = requests.get('https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=15&page=1&sparkline=false&price_change_percentage=1d').json()
    except requests.exceptions.ConnectionError as e:
        raise SystemExit(e)
    if request.user.is_authenticated:
        holdings = Coin.objects.filter(user = request.user)
        userdata = User.objects.get(id=request.user.id)
        return render(request, "VSCrypto/dashboard.html",{
            'apidata':coindata,
            'nums':list(range(0, 14)),
            'userdata':userdata,
            'holdings':holdings
        })
    else:
        return render(request, "VSCrypto/dashboard.html",{
            'apidata':coindata,
            'nums':list(range(0, 14))
        })

def coin(request, id):
    try:
        coindata = requests.get(f'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={id}&order=market_cap_desc&per_page=2&page=1&sparkline=false&price_change_percentage=24h').json()
    except requests.exceptions.ConnectionError as e:
        raise SystemExit(e)
    return render(request, "VSCrypto/coin.html",{
        'apidata':coindata,
    })

@login_required
def buy(request, coin_id):
    if request.method=="POST":
        amt_rqd = float(request.POST["price"]) * float(request.POST["quantity"])
        curbalance = User.objects.get(username = request.user.username).balance
        if amt_rqd <= curbalance:
            try:
                prevcoin = Coin.objects.filter(user = request.user).get(coinid = coin_id)
            except Coin.DoesNotExist:
                prevcoin = None

            if prevcoin:
                """COIN EXISTS ALREADY"""
                Coin.objects.filter(user = request.user).filter(coinid = coin_id).update(buyprice = (float(request.POST["price"])+prevcoin.buyprice)/2, quantity = float(request.POST["quantity"])+prevcoin.quantity)
            else:
                """COIN DOES NOT EXIST ALREADY"""
                Coin.objects.create(user = request.user, coinid = coin_id, buyprice = (float(request.POST["price"])) , quantity = float(request.POST["quantity"]))

            curbalance -= amt_rqd
            User.objects.filter(username = request.user.username).update(balance = curbalance)
            print("TRANSACTION COMPLETE")
            userdata = User.objects.get(id=request.user.id)
            holdings = Coin.objects.filter(user = request.user)
            coindata = requests.get('https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=15&page=1&sparkline=false&price_change_percentage=1d').json()
            return render(request, "VSCrypto/dashboard.html",{
            'apidata':coindata,
            'nums':list(range(0, 14)),
            'message': "Transaction Complete",
            'userdata':userdata,
            'holdings':holdings
        })
        else:
            print("NOT ENOUGH BALANCE")
            userdata = User.objects.get(id=request.user.id)
            holdings = Coin.objects.filter(user = request.user)
            coindata = requests.get('https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=15&page=1&sparkline=false&price_change_percentage=1d').json()
            return render(request, "VSCrypto/dashboard.html",{
            'apidata':coindata,
            'nums':list(range(0, 14)),
            'message': "Transaction Failed",
            'userdata':userdata,
            'holdings':holdings
            })
    else:
        pass

@login_required
def cash(request):
    userdata = User.objects.get(id=request.user.id)
    return render(request, "VSCrypto/cash.html",{
        'nums':list(range(0, 14)),
        'userdata':userdata,
    })

@login_required
def holdings(request):
    holdings = Coin.objects.filter(user = request.user)
    return render(request, "VSCrypto/holdings.html",{
        'nums':list(range(0, 14)),
        'holdings':holdings
    })

@login_required
def sell(request ,id , price ,qty):
    holdings = Coin.objects.filter(user = request.user).get(coinid = id)
    curbalance = User.objects.get(username = request.user.username).balance
    profit = (float(price) * float(qty))
    amt_ret = curbalance + profit
    User.objects.filter(username = request.user.username).update(balance = amt_ret)
    holdings.delete()
    userdata = User.objects.get(id=request.user.id)
    holdings2 = Coin.objects.filter(user = request.user)
    coindata = requests.get('https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=15&page=1&sparkline=false&price_change_percentage=1d').json()
    return render(request, "VSCrypto/dashboard.html",{
        'apidata':coindata,
        'nums':list(range(0, 14)),
        'message': f"Successfully Sold +{profit}",
        'userdata':userdata,
        'holdings':holdings2
    })

def all(request, page):
    try:
        coindata = requests.get(f'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=50&page=${page}&sparkline=false&price_change_percentage=1d').json()
    except requests.exceptions.ConnectionError as e:
        raise SystemExit(e)
    return render(request, "VSCrypto/all.html",{
        'apidata':coindata,
        'nums':list(range(page-1, page+49)),
        'pagep1': page+1
    })

@login_required
def deposit(request):
    if request.method=="POST":
        curbalance = User.objects.get(username = request.user.username).balance
        depositamt = float(request.POST["quantity"])
        balance = curbalance + depositamt
        User.objects.filter(username = request.user.username).update(balance = balance)
        userdata = User.objects.get(id=request.user.id)
        holdings = Coin.objects.filter(user = request.user)
        coindata = requests.get('https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=15&page=1&sparkline=false&price_change_percentage=1d').json()
        return render(request, "VSCrypto/dashboard.html",{
            'apidata':coindata,
            'nums':list(range(0, 14)),
            'message': f"Successfully Deposited {balance}",
            'userdata':userdata,
            'holdings':holdings
        })
    else:
        pass

@login_required
def withdraw(request):
    if request.method=="POST":
        curbalance = User.objects.get(username = request.user.username).balance
        withdrawamount = float(request.POST["quantity"])
        balance = curbalance - withdrawamount
        User.objects.filter(username = request.user.username).update(balance = balance)
        userdata = User.objects.get(id=request.user.id)
        holdings = Coin.objects.filter(user = request.user)
        coindata = requests.get('https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=15&page=1&sparkline=false&price_change_percentage=1d').json()
        return render(request, "VSCrypto/dashboard.html",{
            'apidata':coindata,
            'nums':list(range(0, 14)),
            'message': f"Successfully Withdrew {balance}",
            'userdata':userdata,
            'holdings':holdings
        })
    else:
        pass

def coincall(request, coinid):
    coindata = requests.get(f'https://api.coingecko.com/api/v3/simple/price?ids={coinid}&vs_currencies=usd').json()
    data = coindata.get(f"{coinid}")
    price = data.get("usd")
    return JsonResponse({
        "price":price
    })
    