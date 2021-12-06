from nonebot import on_command, require
from nonebot.rule import T_State
from nonebot.adapters.cqhttp import Bot, MessageEvent, Message, GroupMessageEvent, PrivateMessageEvent
from .data_source import SetSignIn, SignIn, QuerySignIn

rule = require("rule")
CLASS_CADRE = rule.CLASS_CADRE
IS_USER = rule.IS_USER

query_sign_in = on_command("签到情况", aliases={"签到状态"})
set_login_in = on_command("添加签到", aliases={"设置签到"})
set_group_login = on_command("添加群签到")
set_private_login = on_command("添加个人签到", aliases={"添加单独签到"})
login_in = on_command("签到")


# ---------- 发起签到 ----------
async def set_login_in_handle(bot: Bot, event: MessageEvent, state: T_State):
    if await CLASS_CADRE(bot, event, state):
        state["param"] = state["class_cadre"]
        key = event.message
        if key:
            state["key"] = key
    else:
        await set_login_in.finish()


def set_login_in_got(typeof: str):
    """添加签到"""
    async def _(bot: Bot, event: MessageEvent, state: T_State):
        state["key"] = Message(state["key"])
        async with SetSignIn(state["param"]["班级"],
                             state["key"], typeof) as res:
            if not res.existence:
                await set_login_in.finish(res.text())
            else:
                await set_login_in.send(res.text())
    return _


def set_login_in_reset(typeof: str):
    """判断是否重置签到"""
    async def _(bot: Bot, event: MessageEvent, state: T_State):
        if "是" in state["existence"]:
            async with SetSignIn(state["param"]["班级"], state["key"], typeof) as res:
                res.reset_sign_in()
                await set_login_in.finish(res.text())
    return _


set_login_in.handle()(set_login_in_handle)
set_private_login.handle()(set_login_in_handle)
set_group_login.handle()(set_login_in_handle)

set_login_in.got("key", prompt="请输入签到关键字")(set_login_in_got("any"))
set_private_login.got("key", prompt="请输入签到关键字")(set_login_in_got("private"))
set_group_login.got("key", prompt="请输入签到关键字")(set_login_in_got("group"))

set_login_in.got("existence")(set_login_in_reset("any"))
set_private_login.got("existence")(set_login_in_reset("private"))
set_group_login.got("existence")(set_login_in_reset("group"))


# ---------- 签到 ----------
@login_in.handle()
async def login_in_handle(bot: Bot, event: MessageEvent, state: T_State):
    if await IS_USER(bot, event, state):
        if event.message:
            state["key"] = event.message
    else:
        await login_in.finish()


@login_in.got("key", prompt="请输入签到关键字")
async def login_in_got(bot: Bot, event: MessageEvent, state: T_State):
    state["key"] = Message(state["key"])
    with SignIn(
            event.user_id,
            state["user_info"]["姓名"],
            state["user_info"]["班级"],
            state["key"],
            event.message_type) as res:
        await login_in.finish(res.text())


# ---------- 查询签到 ----------
@query_sign_in.handle()
async def query_sign_in_handle(bot: Bot, event: MessageEvent, state: T_State):
    if await CLASS_CADRE(bot, event, state):
        state["param"] = state["class_cadre"]
    else:
        await query_sign_in.finish()


@query_sign_in.got("param")
async def query_sign_in_got(bot: Bot, event: MessageEvent, state: T_State):
    with QuerySignIn(state["param"]["班级"]) as res:
        for msg in res.text():
            await query_sign_in.send(msg)


