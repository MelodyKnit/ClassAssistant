from nonebot import on_command, require
from nonebot.adapters.cqhttp import Bot, MessageEvent
from .data_source import get_url, AddGoods, SelectGoods

add_goods = on_command("更新商品", aliases={"添加商品", "更新列表"})
select_goods = on_command("查看商品", aliases={"商品列表", "兑换列表"})
# purchase = on_command("购买", aliases={"兑换"})
TEACHER = require("permission").TEACHER
IS_USER = require("rule").IS_USER


@add_goods.handle()
async def add_goods_handle(bot: Bot, event: MessageEvent, state: dict):
    if await TEACHER(bot, event):
        url = get_url(event.message)
        if url:
            state["url"] = url
    else:
        await add_goods.finish()


@add_goods.got("url", prompt="请发送在线文档或者链接")
async def add_goods_got(bot: Bot, event: MessageEvent, state: dict):
    url = get_url(state["url"])
    if url:
        async with AddGoods(event.user_id, url) as res:
            await add_goods.finish(res.text())


@select_goods.handle()
async def select_goods_handle(bot: Bot, event: MessageEvent, state: dict):
    if await IS_USER(bot, event, state):
        async with SelectGoods(event.user_id) as res:
            await select_goods.finish(res.text())


# @purchase.handle()
# async def purchase_handle(bot: Bot, event: MessageEvent, state: dict):
#     if await IS_USER(bot, event, state):
#         text = event.get_plaintext()
#         if text:
#             state["param"] = text


# @purchase.got("param", prompt="请输入序号或名称")
# async def purchase_got(bot: Bot, event: MessageEvent, state: dict):
#     if not isinstance(state["param"], list):
#         state["param"] = state["param"].split()
#     if state["param"]:
#         ...


