from nonebot import on_command, require
from nonebot.adapters.cqhttp import Bot, Message, GroupMessageEvent
from nonebot.rule import T_State
from .data_source import QueryUser, AtUser


CLASS_GROUP = require("permission").CLASS_GROUP
query_user = on_command("查询", aliases={"查找", "搜索"})
at_user = on_command("at", aliases={"艾特", "@"})


def get_text(message: Message) -> str:
    """获取文本"""
    for msg in message:
        if msg.type == "text":
            return msg.data.get("text").strip()
        if msg.type == "at":
            return " " + str(msg.data.get("qq"))


@query_user.handle()
async def query_user_handle(bot: Bot, event: GroupMessageEvent, state: T_State):
    """获取查询的用户，如果没有填写查询对象则默认查询自己"""
    if await CLASS_GROUP(bot, event):
        features = get_text(event.message)
        state["param"] = features.split() if features else [event.get_user_id()]
    else:
        await query_user.finish()


@query_user.got("param")
async def query_user_got(bot: Bot, event: GroupMessageEvent, state: T_State):
    async with QueryUser(state["param"], event.group_id) as res:
        await query_user.finish(res.text())


@at_user.handle()
async def at_user_handle(bot: Bot, event: GroupMessageEvent, state: T_State):
    if await CLASS_GROUP(bot, event):
        features = get_text(event.message)
        if features:
            state["param"] = features.split()
    else:
        await query_user.finish()


@at_user.got("param", prompt="请输入您需要at的成员名称/序号/qq/学号。")
async def at_user_got(bot: Bot, event: GroupMessageEvent, state: T_State):
    if isinstance(state["param"], str):
        state["param"] = state["param"].split()
    if state["param"]:
        async with AtUser(state["param"], event.group_id) as res:
            if not res.is_err:
                await at_user.finish(res.text())

