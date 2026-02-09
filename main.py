import asyncio
import datetime
import json
import os
import queue
import random
import re
import subprocess
import sys
import threading

import aiohttp
import discord
import streamlit as st
from discord import app_commands
from discord.ext import commands, tasks
from discord.utils import get
from dotenv import load_dotenv

import server
from acb import *
from guild import *

load_dotenv()

USERNAME = os.environ.get("username")
PASSWORD = os.environ.get("password")

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
VIETTELS = "032, 033, 034, 035, 036, 037, 038, 039, 096, 097, 098, 086"
VIETTELS = VIETTELS.split(",")
VINAPHONES = " 091, 094, 088, 081, 082, 083, 084, 085"
VINAPHONES = VINAPHONES.split(",")
VIETNAMOBILE = "052, 056, 058, 092"
VIETNAMOBILE = VIETNAMOBILE.split(",")
HEADERS = []
THREADS = []
USERNAMES = []
GUILDID = 1236962671824211998
RESULT = None


def correctSingleQuoteJSON(s):
    rstr = ""
    escaped = False

    for c in s:
        if c == "'" and not escaped:
            c = '"'  # replace single with double quote

        elif c == "'" and escaped:
            rstr = rstr[:-1]  # remove escape character before single quotes

        elif c == '"':
            c = "\\" + c  # escape existing double quotes

        escaped = c == "\\"  # check for an escape character
        rstr += c  # append the correct json

    return rstr


if "log_queue" not in st.session_state:
    st.session_state["log_queue"] = queue.Queue()

if "logs" not in st.session_state:
    st.session_state["logs"] = []

if "task_running" not in st.session_state:
    st.session_state["task_running"] = False
processed_thread = set()
pause_watching = False

INFO = False
BASE_URL = "https://bot-py-8t7nnjtaylrcjeqj8tevuh.streamlit.app/"


def myStyle(log_queue):
    MY_GUILD = discord.Object(id=1236962671824211998)  # replace with your guild id

    @client.event
    async def on_ready():
        global INFO, RESULT
        try:
            req = requests.get("http://localhost:8888")
            print("Client closed")
            log_queue.put(
                ("error", f"Client closed with status code {req.status_code}")
            )
            sys.exit("Exited")
        except Exception as error:
            print(error)
            server.b()
            guild = client.get_guild(GUILDID)
            stop = False
            while not stop:
                rs = await login(USERNAME, PASSWORD)
                RESULT = await getBasic(guild)
                if rs:
                    stop = True
                    INFO = rs
                    if not getTransAcb.is_running():
                        getTransAcb.start(guild)
                log_queue.put(("info", "Trying login again"))
                await asyncio.sleep(3)

    @client.event
    async def on_disconnect():
        global RESULT
        if RESULT:
            acbThread = None
            for thread in RESULT["banksCh"].threads:
                if "acb" in thread.name:
                    acbThread = thread
            if acbThread:
                msgs = [msg async for msg in acbThread.history()]
                if len(msgs) > 0:
                    old = re.search(".*Sessions are `(.*?)`.*", msgs[0].content).group(
                        1
                    )
                    i = int(old) - 1 if int(old) > 0 else 0
                    await msgs[0].edit(content="Sessions are `" + str(i) + "` actived")

    @tasks.loop(seconds=1)
    async def getTransAcb(guild):
        global INFO
        print("getTransAcb is running")
        log_queue.put(("info", "getTransAcb is running"))
        if INFO:
            try:
                rs1 = await getListAccount(INFO)
                if rs1:
                    for item in rs1["list"]:
                        list = await getBalance(INFO, item["accountNumber"])
                        if list:
                            basic = await getBasic(guild)
                            threads = basic["acbCh"].threads + [
                                thread
                                async for thread in basic["acbCh"].archived_threads()
                            ]
                            if list:
                                data = list["data"][::-1]
                                for item in data:
                                    applied_tags = []
                                    if str(item["activeDatetime"]) not in str(threads):
                                        tags = basic["acbCh"].available_tags
                                        st = ""
                                        if item["type"].lower() == "in":
                                            for tag in tags:
                                                if (
                                                    "in" in tag.name.lower()
                                                    or "chuyển đến" in tag.name.lower()
                                                ):
                                                    applied_tags.append(tag)
                                        else:
                                            for tag in tags:
                                                if (
                                                    "out" in tag.name.lower()
                                                    or "chuyển đi" in tag.name.lower()
                                                ):
                                                    applied_tags.append(tag)
                                            if (
                                                "bankName" in item
                                                and item["bankName"] != ""
                                            ):
                                                st += (
                                                    "\nĐến ngân hàng: **"
                                                    + item["bankName"]
                                                    + "**\n"
                                                )
                                            if (
                                                "receiverAccountNumber" in item
                                                and item["receiverAccountNumber"] != ""
                                            ):
                                                st += (
                                                    "\nĐến số tài khoản: **"
                                                    + item["receiverAccountNumber"]
                                                    + "**"
                                                )
                                            if (
                                                "receiverName" in item
                                                and item["receiverName"] != ""
                                            ):
                                                st += (
                                                    "\nĐến chủ tài khoản: **"
                                                    + item["receiverName"]
                                                    + "**"
                                                )
                                        allowed_mentions = discord.AllowedMentions(
                                            everyone=True
                                        )
                                        amount = str(item["amount"]).split(".")[0]
                                        amount = [f"{cur:,}" for cur in [int(amount)]][
                                            0
                                        ]
                                        time = datetime.datetime.fromtimestamp(
                                            item["activeDatetime"] / 1000
                                        )
                                        day = (
                                            time.day
                                            if time.day > 9
                                            else "0" + str(time.day)
                                        )
                                        month = (
                                            time.month
                                            if time.month > 9
                                            else "0" + str(time.month)
                                        )
                                        hour = (
                                            time.hour
                                            if time.hour > 9
                                            else "0" + str(time.hour)
                                        )
                                        minute = (
                                            time.minute
                                            if time.minute > 9
                                            else "0" + str(time.minute)
                                        )
                                        second = (
                                            time.second
                                            if time.second > 9
                                            else "0" + str(time.second)
                                        )
                                        timestr = f"{day}/{month}/{time.year} {hour}:{minute}:{second}"
                                        thread = await basic["acbCh"].create_thread(
                                            name=(
                                                "+ "
                                                if item["type"].lower() == "in"
                                                else "- "
                                            )
                                            + amount
                                            + " "
                                            + item["currency"]
                                            + "/ "
                                            + str(item["activeDatetime"]),
                                            content="\nSố tiền: **"
                                            + amount
                                            + " "
                                            + item["currency"]
                                            + "**\nNội dung: **"
                                            + item["description"]
                                            + "**\nBiến động trên STK: **"
                                            + str(item["account"])
                                            + "**\nThời điểm: **"
                                            + timestr.split(" ")[1]
                                            + "** ngày **"
                                            + timestr.split(" ")[0]
                                            + "**"
                                            + st
                                            + "\n@everyone",
                                            applied_tags=applied_tags,
                                        )
                else:
                    rs = await login(USERNAME, PASSWORD)
                    if rs:
                        INFO = rs
            except Exception as error:
                print(error)
                log_queue.put(("error", str(error)))
                rs = await login(USERNAME, PASSWORD)
                if rs:
                    INFO = rs

    client.run(os.environ.get("botToken"))


thread = None


@st.cache_resource
def initialize_heavy_stuff():
    global thread
    # Đây là phần chỉ chạy ĐÚNG 1 LẦN khi server khởi động (hoặc khi cache miss)
    with st.spinner("running your scripts..."):
        thread = threading.Thread(target=myStyle, args=(st.session_state.log_queue,))
        thread.start()
        print(
            "Heavy initialization running..."
        )  # bạn sẽ thấy log này chỉ 1 lần trong console/cloud log

        return {
            "model": "loaded_successfully",
            "timestamp": time.time(),
            "db_status": "connected",
        }


# Trong phần chính của app
st.title("my style")

# Dòng này đảm bảo: chạy 1 lần duy nhất, mọi user đều dùng chung kết quả
result = initialize_heavy_stuff()

st.success("The system is ready!")
st.write("Result:")
st.json(result)
with st.status("Processing...", expanded=True) as status:
    placeholder = st.empty()
    logs = []
    while (thread and thread.is_alive()) or not st.session_state.log_queue.empty():
        try:
            level, message = st.session_state.log_queue.get_nowait()
            logs.append((level, message))

            with placeholder.container():
                for lvl, msg in logs:
                    if lvl == "info":
                        st.write(msg)
                    elif lvl == "success":
                        st.success(msg)
                    elif lvl == "error":
                        st.error(msg)

            time.sleep(0.2)
        except queue.Empty:
            time.sleep(0.3)

    status.update(label="Hoàn thành!", state="complete", expanded=False)
