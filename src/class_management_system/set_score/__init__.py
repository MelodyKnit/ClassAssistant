from nonebot import on_command, require
from nonebot.adapters.cqhttp import Bot, MessageEvent
from .data_source import SetScore, config, GiftScore

rule = require("rule")
IS_USER = rule.IS_USER
CLASS_CADRE = rule.CLASS_CADRE

add_score = on_command("加分", aliases={"添加分数", "减分", "扣分", "设置分数"})
gift_score = on_command("转让", aliases={"赠与"})


@add_score.handle()
async def add_score_handler(bot: Bot, event: MessageEvent, state: dict):
    if (await CLASS_CADRE(bot, event, state)) and state["class_cadre"]["职位"] in config.score:
        text = event.get_plaintext()
        if text:
            state["param"] = text.split()
    else:
        await add_score.finish()


@add_score.got("param", prompt="请输入成员名称与分数")
async def add_score_got(bot: Bot, event: MessageEvent, state: dict):
    text = event.get_plaintext()
    if text:
        async with SetScore(state["class_cadre"]["班级"], text) as res:
            await add_score.finish(res.text())


@gift_score.handle()
async def gift_score_handle(bot: Bot, event: MessageEvent, state: dict):
    if await IS_USER(bot, event, state):
        text = event.get_plaintext()
        if text:
            state["param"] = text


@gift_score.got("param", prompt="请输入需要转让的那一位同学姓名与数量")
async def gift_score_got(bot: Bot, event: MessageEvent, state: dict):
    text = event.get_plaintext()
    if text:
        async with GiftScore(state["user_info"]["班级"], event.user_id, state["user_info"]["分数"], text) as res:
            await gift_score.finish(res.text())

