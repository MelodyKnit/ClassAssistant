from nonebot import on_command, require
from .data_source import InsertUser
from nonebot.adapters.cqhttp import Bot, GroupMessageEvent, Message
from nonebot.rule import T_State
from typing import Union
import re

rule = require("rule")
permission = require("permission")
TEACHER = permission.TEACHER
MASTER = rule.MASTER
push_user = on_command("导入班级信息", aliases={"导入班级"})


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


def get_text(message: Message):
    """获取文本"""
    for msg in message:
        if msg.type == "text":
            return msg.data.get("text").strip()


@push_user.handle()
async def push_user_handler(bot: Bot, event: GroupMessageEvent, state: T_State):
    if await MASTER(bot, event, state):
        url = get_url(event.message)
        if url:
            state["param"] = url
    else:
        await push_user.finish()


@push_user.got("param", "请转发腾讯在线文档，或者在线文档的链接！！！")
async def push_user_got(bot: Bot, event: GroupMessageEvent, state: T_State):
    url = get_url(state["param"])
    if url:
        # 获取班级名称
        class_name = state["all_group"]["class_name"][state["all_group"]["class_group"].index(event.group_id)]
        async with InsertUser(url, class_name) as res:
            await push_user.finish(res.text())

