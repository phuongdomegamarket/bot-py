import asyncio
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
        res = requests.post(url, headers=headers, json=data)
        if res.status_code < 400:
            js = res.json()
            headers["authorization"] = "Bearer " + js["refreshToken"]
            refreshTk = js["refreshToken"]
            url = "https://apiapp.acb.com.vn/mb/v2/auth/refresh"
            res = requests.post(url, headers=headers)
            if res.status_code < 400:
                js = res.json()
                headers["authorization"] = "Bearer " + js["accessToken"]
                print(user + " login success")
                return {
                    "headers": headers,
                    "refreshTk": refreshTk,
                    "username": user,
                }
        return False
        # async with aiohttp.ClientSession(
        #     timeout=timeout, cookie_jar=aiohttp.CookieJar(), connector=connector
        # ) as session:
        #     try:
        #         async with session.post(
        #             url, headers=headers, json=data, ssl=False
        #         ) as res:
        #             if res.status < 400:
        #                 js = await res.json()
        #                 headers["authorization"] = "Bearer " + js["refreshToken"]
        #                 refreshTk = js["refreshToken"]
        #                 url = "https://apiapp.acb.com.vn/mb/v2/auth/refresh"
        #                 async with aiohttp.ClientSession(
        #                     cookie_jar=aiohttp.CookieJar()
        #                 ) as session:
        #                     async with session.post(url, headers=headers) as res:
        #                         url = "https://apiapp.acb.com.vn/mb/legacy/ss/cs/bankservice/transfers/list/account-payment"
        #                         if res.status < 400:
        #                             js = await res.json()
        #                             headers["authorization"] = (
        #                                 "Bearer " + js["accessToken"]
        #                             )
        #                             print(user + " login success")
        #                             return {
        #                                 "headers": headers,
        #                                 "refreshTk": refreshTk,
        #                                 "username": user,
        #                             }
        #             return False
        #     except Exception as err:
        #         print(err)
        #         return False
    except Exception as err:
        print(err)
        return None


async def getRefreshTk(headers):
    try:
        url = "https://apiapp.acb.com.vn/mb/auth/refresh"
        headers["authorization"] = "Bearer " + headers["refreshTk"]
        # res = requests.post(url, headers=headers)
        # if res.status_code < 400:
        #     js = res.json()
        #     headers["authorization"] = "Bearer " + js["accessToken"]
        #     print(headers["username"] + " get refresh token success")
        #     return {
        #         headers[""] + "headers": headers,
        #         "refreshTk": headers["refreshTk"],
        #         "username": headers["username"],
        #     }
        # return False
        timeout = aiohttp.ClientTimeout(total=None, connect=None, sock_connect=None)
        async with aiohttp.ClientSession(
            cookie_jar=aiohttp.CookieJar(), timeout=timeout
        ) as session:
            async with session.post(url, headers=headers, ssl=False) as res:
                if res.status < 400:
                    js = await res.json()
                    headers["authorization"] = "Bearer " + js["accessToken"]
                    print(headers["username"] + " get refresh token success")
                    return {
                        headers[""] + "headers": headers,
                        "refreshTk": headers["refreshTk"],
                        "username": headers["username"],
                    }
    except Exception as error:
        print(error)
        return False


async def getListAccount(headers):
    try:
        url = "https://apiapp.acb.com.vn/mb/legacy/ss/cs/bankservice/transfers/list/account-payment"
        # res = requests.get(url, headers=headers["headers"])
        # if res.status_code < 400:
        #     js =  res.json()
        #     print(headers["username"] + " get list account success")
        #     return {"list": js["data"]}
        # return False
        timeout = aiohttp.ClientTimeout(total=None, connect=None, sock_connect=None)
        async with aiohttp.ClientSession(
            cookie_jar=aiohttp.CookieJar(), timeout=timeout
        ) as session:
            async with session.get(url, headers=headers["headers"], ssl=False) as res:
                if res.status < 400:
                    js = await res.json()
                    print(headers["username"] + " get list account success")
                    return {"list": js["data"]}
            return False
    except Exception as error:
        print(error)
        return False


async def getBalance(headers, id):
    try:
        url = "https://apiapp.acb.com.vn/mb/legacy/ss/cs/person/transaction-history/list?account=15895127&transactionType=&from=&to=&min=&max="
        # res = requests.get(url, headers=headers["headers"])
        # if res.status_code < 400:
        #     js =  res.json()
        #     print(headers["username"] + " get balance success")
        #     return {"data": js["data"]}
        # return False
        timeout = aiohttp.ClientTimeout(total=None, connect=None, sock_connect=None)
        async with aiohttp.ClientSession(
            cookie_jar=aiohttp.CookieJar(), timeout=timeout
        ) as session:
            async with session.get(url, headers=headers["headers"], ssl=False) as res:
                if res.status < 400:
                    js = await res.json()
                    print(headers["username"] + " get balance success")
                    return {"data": js["data"]}
                return False
    except Exception as error:
        print(error)
        return False
