from nonebot import on_command, require
from nonebot.rule import T_State
from .data_source import get_url, GetExcelNotUser, CheckUser
from nonebot.adapters.cqhttp import Bot, GroupMessageEvent

push_user_info = on_command("未填写", aliases={"查表格", "查表", "为填表"})
check_user = on_command("核对信息", aliases={"核验", "检查", "检查信息"})
deep_check_user = on_command("深度检查", aliases={"严格检查", "深度核对"})
super_check_user = on_command("超级核对", aliases={"超级检查"})
IS_USER = require("rule").IS_USER


# 添加班级成员需要按群添加，因为群内唯一群号绑定一个班级名
@push_user_info.handle()
async def _push_user_info_handle(bot: Bot, event: GroupMessageEvent, state: T_State):
    if await IS_USER(bot, event, state):
        url = get_url(event.message)
        if url:
            state["url"] = url
    else:
        await push_user_info.finish()


# 未接受到班级表格时
@push_user_info.got("url", prompt="请发送班级表格")
async def _push_user_info_got(bot: Bot, event: GroupMessageEvent, state: T_State):
    url = get_url(state["url"])
    if url:
        async with GetExcelNotUser(state["user_info"]["班级"], url) as res:
            await push_user_info.finish(res.text())


def set_url(matcher):
    @matcher.handle()
    async def _(bot: Bot, event: GroupMessageEvent, state: T_State):
        if await IS_USER(bot, event, state):
            url = get_url(event.message)
            if url:
                state["url"] = url
        else:
            await matcher.finish()


# 检查班级信息
set_url(check_user)
set_url(deep_check_user)
set_url(super_check_user)


# 未接受到班级表格时
@check_user.got("url", prompt="请发送班级表格")
async def _push_user_info_got(bot: Bot, event: GroupMessageEvent, state: T_State):
    url = get_url(state["url"])
    if url:
        async with CheckUser(state["user_info"]["班级"], url) as res:
            res.select_info()
            await check_user.finish(res.text())


# 未接受到班级表格时
@deep_check_user.got("url", prompt="请发送班级表格")
async def _push_user_info_got(bot: Bot, event: GroupMessageEvent, state: T_State):
    url = get_url(state["url"])
    if url:
        async with CheckUser(state["user_info"]["班级"], url) as res:
            res.deep_select_info()
            await deep_check_user.finish(res.text())


# 未接受到班级表格时
@super_check_user.got("url", prompt="请发送班级表格")
async def _push_user_info_got(bot: Bot, event: GroupMessageEvent, state: T_State):
    url = get_url(state["url"])
    if url:
        async with CheckUser(state["user_info"]["班级"], url) as res:
            res.super_select_info()
            await super_check_user.finish(res.text())
