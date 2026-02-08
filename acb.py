import base64
import datetime
import json
import os
import random
import re
import time
from urllib.parse import unquote

import aiohttp
import requests
from bs4 import BeautifulSoup as Bs4


async def login(user, password):
    try:
        url = "https://apiapp.acb.com.vn/mb/v2/auth/tokens"
        data = {
            "username": user,
            "password": password,
            "clientId": "iuSuHYVufIUuNIREV0FB9EoLn9kHsDbm",
        }
        headers = {"user-agent": "ACB-MBA/5 CFNetwork/1325.0.1 Darwin/21.1.0"}
        req = requests.post(url, headers=headers, json=data)
        print(req)
        async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar()) as session:
            async with session.post(url, headers=headers, json=data) as res:
                if res.status < 400:
                    js = await res.json()
                    headers["authorization"] = "Bearer " + js["refreshToken"]
                    refreshTk = js["refreshToken"]
                    url = "https://apiapp.acb.com.vn/mb/v2/auth/refresh"
                    async with aiohttp.ClientSession(
                        cookie_jar=aiohttp.CookieJar()
                    ) as session:
                        async with session.post(url, headers=headers) as res:
                            url = "https://apiapp.acb.com.vn/mb/legacy/ss/cs/bankservice/transfers/list/account-payment"
                            if res.status < 400:
                                js = await res.json()
                                headers["authorization"] = "Bearer " + js["accessToken"]
                                print(user + " login success")
                                return {
                                    "headers": headers,
                                    "refreshTk": refreshTk,
                                    "username": user,
                                }
                return False
    except Exception as err:
        print(err)
        return None


async def getRefreshTk(headers):
    url = "https://apiapp.acb.com.vn/mb/auth/refresh"
    headers["authorization"] = "Bearer " + headers["refreshTk"]
    async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar()) as session:
        async with session.post(url, headers=headers) as res:
            if res.status < 400:
                js = await res.json()
                headers["authorization"] = "Bearer " + js["accessToken"]
                print(headers["username"] + " get refresh token success")
                return {
                    headers[""] + "headers": headers,
                    "refreshTk": headers["refreshTk"],
                    "username": headers["username"],
                }


async def getListAccount(headers):
    url = "https://apiapp.acb.com.vn/mb/legacy/ss/cs/bankservice/transfers/list/account-payment"
    async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar()) as session:
        async with session.get(url, headers=headers["headers"]) as res:
            if res.status < 400:
                js = await res.json()
                print(headers["username"] + " get list account success")
                return {"list": js["data"]}
        return False


async def getBalance(headers, id):
    url = "https://apiapp.acb.com.vn/mb/legacy/ss/cs/person/transaction-history/list?account=15895127&transactionType=&from=&to=&min=&max="
    async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar()) as session:
        async with session.get(url, headers=headers["headers"]) as res:
            if res.status < 400:
                js = await res.json()
                print(headers["username"] + " get balance success")
                return {"data": js["data"]}
            return False
