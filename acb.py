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
            "deviceId": "EBE09644-18AF-408F-B642-8C23F5D9D6B9",
        }
        headers = {"user-agent": "ACB-MBA/17 CFNetwork/1325.0.1 Darwin/21.1.0"}
        # res = requests.post(url, headers=headers, json=data)
        # if res.status_code < 400:
        #     js = res.json()
        #     headers["authorization"] = "Bearer " + js["refreshToken"]
        #     refreshTk = js["refreshToken"]
        #     url = "https://apiapp.acb.com.vn/mb/v2/auth/refresh"
        #     res = requests.post(url, headers=headers)
        #     if res.status_code < 400:
        #         js = res.json()
        #         headers["authorization"] = "Bearer " + js["accessToken"]
        #         print(user + " login success")
        #         return {
        #             "headers": headers,
        #             "refreshTk": refreshTk,
        #             "username": user,
        #         }
        # return False
        timeout = aiohttp.ClientTimeout(total=None, connect=None, sock_connect=None)
        async with aiohttp.ClientSession(
            timeout=timeout, cookie_jar=aiohttp.CookieJar()
        ) as session:
            try:
                async with session.post(
                    url, headers=headers, json=data, ssl=False
                ) as res:
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
                                    headers["authorization"] = (
                                        "bearer " + js["accessToken"]
                                    )
                                    print(user + " login success")
                                    return {
                                        "headers": headers,
                                        "refreshTk": refreshTk,
                                        "username": user,
                                    }
                    return False
            except Exception as err:
                print(err)
                print("can't login")
                return False
    except Exception as err:
        print(err)
        print("can't login")
        return None


async def getRefreshTk(headers):
    try:
        url = "https://apiapp.acb.com.vn/mb/v2/auth/refresh"
        headers["headers"] = {
            **headers["headers"],
            "authorization": "Bearer " + headers["refreshTk"],
        }
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
            async with session.post(url, headers=headers["headers"], ssl=False) as res:
                if res.status < 400:
                    js = await res.json()
                    headers["authorization"] = "Bearer " + js["accessToken"]
                    print(headers["username"] + " get refresh token success")
                    return {
                        "refreshTk": headers["refreshTk"],
                        "username": headers["username"],
                    }
    except Exception as error:
        print(error)
        print("can't get refresh token")
        return False


async def getListAccount(headers):
    try:
        if headers:
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
                async with session.get(
                    url, headers=headers["headers"], ssl=False
                ) as res:
                    if res.status < 400:
                        js = await res.json()
                        print(headers["username"] + " get list account success")
                        return {"list": js["data"]}
                return False
    except Exception as error:
        print(error)
        print("can't get list account")
        return False


async def getBalance(headers, id=None):
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
            async with session.get(
                url,
                headers=headers["headers"],
                ssl=False,
            ) as res:
                print(await res.text())
                if res.status < 400:
                    js = await res.json()
                    print(headers["username"] + " get balance success")
                    return {"data": js["data"]}
                return False
    except Exception as error:
        print(error)
        print("can't get balance")
        return False


async def getNotifications(headers, size=20):
    try:
        url = f"https://apiapp.acb.com.vn/mb/legacy/ss/cs/bankservice/v2/notifications?page=0&size={size}&language=en"
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
            async with session.get(
                url,
                headers=headers["headers"],
                ssl=False,
            ) as res:
                if res.status < 400:
                    js = await res.json()
                    print(headers["username"] + " get notifications success")
                    return {"data": js["data"]}
                return False
    except Exception as error:
        print(error)
        print("can't get notification")
        return False


def normalize_notification(notification: dict) -> dict:
    message = notification["message"]

    direction = (
        "in"
        if re.search(r"\+\s*[\d,]+", message)
        else "out"
        if re.search(r"-\s*[\d,]+", message)
        else "unknown"
    )

    amount = int(notification.get("amount", 0))

    # Số tài khoản: "Acc 15895127(VND)"
    acc_match = re.search(r"Acc\s+(\d+)", message)
    account = acc_match.group(1) if acc_match else None

    # Tên đối tác: "Transaction: BUI THANH TRUNG chuyen tien ..."
    # hoặc "QR - TRAN THI DOAN Chuyen tien ..."
    name_match = re.search(
        r"Transaction:\s*(?:QR\s*-\s*)?([A-ZÀ-Ỹ\s]+?)\s+[Cc]huyen tien",
        message,
    )
    receiver_name = name_match.group(1).strip() if name_match else None

    return {
        "account": account,
        "type": direction,
        "amount": amount,
        "currency": "VND",
        "description": message,  # notification không có field description riêng, dùng luôn message
        "activeDatetime": notification[
            "createdAt"
        ],  # đã là epoch ms sẵn, khỏi cần parse lại
        "bankName": None,  # notification không có sẵn info ngân hàng đối tác
        "receiverAccountNumber": None,  # không có trong message, muốn có phải parse thêm nếu ACB show ra
        "receiverName": receiver_name,
    }
