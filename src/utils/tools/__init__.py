import re
from nonebot import export
from nonebot.adapters.cqhttp import Message
from .data_source import GetDocsSheet
from .config import Config
from .watermark import Watermark
from typing import Union


def re_docs(text: str) -> str:
    return re.search(r"https://docs.qq.com/sheet/\S[^\"']+", str(text).replace("\\", ""), re.I).group()


def get_url(message: Union[Message, str]) -> str:
    url = None
    if isinstance(message, Message):
        for msg in message:
            if msg.type == "json" or msg.type == "xml":
                url = re_docs(msg.data["data"])
            elif msg.type == "text":
                url = re_docs(msg.data["text"])
            if url:
                return url
    else:
        return re_docs(message)


export = export()
export.GetDocsSheet = GetDocsSheet
export.Watermark = Watermark
export.get_url = get_url
export.re_docs = re_docs
