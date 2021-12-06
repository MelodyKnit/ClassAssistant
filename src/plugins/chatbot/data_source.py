from aiohttp import ClientSession
from nonebot import require
from pandas import DataFrame
from nonebot.adapters.cqhttp import Message
from json import dumps, loads
from random import choice
from typing import List

tools = require("tools")
readfile = require("readfile").ReadFile("data", "chatword")
base_url = "http://i.itpk.cn/api.php"


def get_params(msg: str):
    return {
        "question": msg,
        "limit": 8,
        "api_key": "1447d08d8e018247e2ce829e9d0380e8",
        "api_secret": "p782g4wij4b0"
    }


GetDocsSheet = tools.GetDocsSheet
get_url = tools.get_url
bot_chat: dict = {
    "words": []
}


def chat_sorted(words: dict) -> List:
    return [list(i) for i in sorted(words.items(), key=lambda x: -len(x[0]))]


class AddChatWord:
    def __init__(self, url: str):
        self.url = url
        self.reply = ""

    async def get_sheet(self):
        """获取腾讯文档"""
        async with GetDocsSheet(self.url) as res:
            return res

    async def __aenter__(self):
        """
        从腾讯文档中获取数据
        取出转为dafaframe的数据
        提取词库
        保存到本地
        """
        self.sheet = await self.get_sheet()
        self.data: dict = self.sheet.data
        self.df: DataFrame = self.sheet.data
        self.words = self.chat_word()
        await self.save()
        self.reply = "词库更新成功。"
        return self

    def chat_word(self):
        """
        提取词库整理成字典
        再将字典排序转为列表
        """
        words = {word["关键字"]: [txt for txt in word['随机回复词1': "随机回复词20"] if txt] for i, word in self.df.iterrows()}
        return [list(i) for i in sorted(words.items(), key=lambda x: -len(x[0]))]

    def text(self):
        return Message(self.reply)

    async def save(self):
        """
        将数据保存到本地
        """
        bot_chat["words"] = self.words
        await readfile.write("chat_word.json", dumps(self.words))

    async def __aexit__(self, *args):
        ...


class BotChat:
    def __init__(self, word: str):
        self.word = word

    @staticmethod
    async def data_in_msg(msg: str):
        data = await readfile.read("data.json")
        for i in data:
            if i in msg:
                return choice(data[i])

    @staticmethod
    async def get_message_reply(msg: str):
        async with ClientSession() as session:
            async with session.get(url=base_url, params=get_params(msg)) as resp:
                try:
                    text = loads((await resp.text()).encode("utf-8"))
                    try:
                        return text["content"]
                    except KeyError:
                        return "抱歉，为对数据进行整理目前无法使用"
                except ValueError:
                    return await resp.text()

    @staticmethod
    async def get_words():
        """
        从全局变量中查看是否存在词库
        如果不存在则从本地取出
        :return:
        """
        words = bot_chat["words"]
        if not words:
            words = loads(await readfile.read("data.json"))
            bot_chat["words"] = words
        return words

    async def text(self):
        for i in [
            self.data_in_msg,
            self.get_message_reply
        ]:
            msg = await i(self.word)
            if msg:
                return msg

    async def __aenter__(self):
        # self.words = await self.get_words()
        return self

    async def __aexit__(self, *args):
        ...
