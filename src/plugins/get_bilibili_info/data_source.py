from aiohttp import ClientSession
from nonebot.adapters.cqhttp import MessageSegment, Message
from .config import Config
from typing import Optional, Union
from asyncio import get_event_loop
from pprint import pprint
import re

BV = "bvid"
AV = "aid"
urls = Config()


async def get_link_redirection(url):
    async with ClientSession() as session:
        async with session.get(url) as reply:
            return str(reply.url)


class MessageBar(Message):
    def __getattr__(self, item):
        return lambda *args, **kwargs: self.append(getattr(MessageSegment, item)(*args, **kwargs))


""" ====== 获取视频信息 ====== """


class GetVideoInfo:
    def __init__(self, vid):
        self.vid: str = vid
        self.raw_data: Optional[dict] = None
        self.data: Optional[dict] = None
        self.code: Optional[int] = None
        self.url = urls.video_url

    def params(self) -> dict:
        """
        将id号进行分析是bv还是av号，然后将号转为各自的参数字典
        :return: dict
        """
        if re.match(r"av", self.vid, re.I):
            return {AV: re.sub("av", "", self.vid, flags=re.I)}
        elif re.match(r"bv", self.vid, re.I):
            return {BV: self.vid}
        return {}

    def text(self) -> Union[Message, None]:
        """将json数据转为可读性高的Message实列"""
        if self.code == 0 and self.data:
            stat = self.data['stat']
            reply = (MessageBar()
                     .text(f"{self.data['title']}\n"
                           f"{'-' * 16}\n"
                           f"作者(up): {self.data['owner']['name']}\n"
                           f"作者id: {self.data['owner']['mid']}\n"
                           f"{'-' * 16}\n"
                           f"aid: av{self.data['aid']}\n"
                           f"bvid: {self.data['bvid']}\n"
                           f"cid: {self.data['cid']}\n")
                     .image(self.data["pic"])
                     .text(f"\n播放量: {stat['view']} | 投币数: {stat['coin']} | 点赞数: {stat['like']}"
                           f"\n弹幕数: {stat['danmaku']} | 收藏数: {stat['favorite']} | 评论数: {stat['reply']}"
                           f"\n{'-' * 16}"
                           f"\n{self.data['desc']}\n"
                           f"链接: {self.url}"))
            return reply
        return None

    async def get(self):
        """获取数据"""
        async with self.session.get(urls.video_info_url, params=self.params()) as res:
            data = await res.json()
            self.raw_data = data
            self.url += self.vid
            self.code = data["code"]
            self.data = data["data"] if self.code == 0 else self.data

    async def __aenter__(self):
        self.session = ClientSession()
        await self.get()
        return self

    async def close(self):
        await self.session.close()

    async def __aexit__(self, *args):
        await self.close()


""" ====== 获取用户信息 ====== """


class GetUserInfo:
    def __init__(self, username: str):
        self.username: str = username
        self.url: Optional[str] = None
        self.code: Optional[int] = None
        self.data: Optional[dict] = None
        self.params: Optional[dict] = None

    def user_silence(self):
        """查看用户是否被封"""
        return "\n账号状态: 被封" if self.data["silence"] else ""

    def live_status(self):
        """查看用户是否在直播"""
        live_room = self.data["live_room"]
        if live_room["liveStatus"]:
            return f"\n这位UP正在直播中-直通车: {urls.bili_live_url}{live_room['roomid']}"
        return ""

    def text(self) -> Message:
        return (MessageBar()
                .text(self.data["name"])
                .text(f"\n性别: {self.data['sex']}"
                      f"\n生日: {self.data['birthday'] or '不知道'}"
                      f"\n等级: level{self.data['level']}"
                      f"\n用户id: {self.username}"
                      f"{self.user_silence()}")
                .image(self.data["face"])
                .text(f"\n简介: {self.data['sign']}"
                      f"\n友情链接: {urls.user_url + self.username}"
                      f"{self.live_status()}"))

    async def get_user_info(self):
        """
        获取用户信息
        判断数据是用户id还是用户名称，如果不是用户id则搜索用户并获取用户列表中的第一位作
        获取到第一位用户的id后利用id再次发送请求获取改用户的详细信息
        """
        if self.username.isdigit():
            self.url = urls.user_info_url
            self.params = {"mid": self.username}
            await self.get()
        else:
            self.url = urls.user_name_search_url
            self.params = {
                "search_type": "bili_user",
                "keyword": self.username,
                "changing": "mid",
                "page": 1,
            }
            await self.get()
            self.username = str(self.data["result"][0]["mid"])
            await self.get_user_info()

    async def get(self):
        async with self.session.get(self.url, params=self.params) as reply:
            info = await reply.json()
            self.code = info["code"]
            self.data = info["data"] if self.code == 0 else self.data

    async def __aenter__(self):
        self.session = ClientSession()
        await self.get_user_info()
        return self

    async def close(self):
        await self.session.close()

    async def __aexit__(self, *args):
        await self.close()
