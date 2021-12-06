from nonebot import on_command, require
from nonebot.rule import T_State
from nonebot.adapters.cqhttp import Bot, MessageEvent, Message, GroupMessageEvent
from .data_source import AddScoreLog, SaveDialog, GetMessage, ExportProve

add_log = on_command("德育", aliases={"德育分"})
export_log = on_command("导出德育")
export_prove = on_command("导出证明")

rule = require("rule")
IS_USER = rule.IS_USER
CLASS_CADRE = rule.CLASS_CADRE
DORM_ADMIN = rule.DORM_ADMIN


def get_names(message: str):
    names = message.split(" ")
    new_names = []
    for name in names:
        if name:
            new_names.append(name)
    return new_names


@add_log.handle()
async def add_log_handle(bot: Bot, event: MessageEvent, state: T_State):
    """拆分出姓名"""
    if await IS_USER(bot, event, state):
        users = event.get_plaintext().split()
        state["users"] = None
        if users:
            if await CLASS_CADRE(bot, event, state):
                state["users"] = users
            else:
                await add_log.finish("歪，你不是班干部不能在后面写别人名字呢！")
    else:
        await add_log.finish()


@add_log.got("msg", prompt="说明一下这是什么事情吧。 ^_^")
async def add_log_got(bot: Bot, event: MessageEvent, state: T_State):
    message = GetMessage(Message(state["msg"]))
    if message.images:
        state["images"] = message.images
    if message.text:
        state["msg"] = message.text
    else:
        await add_log.reject(Message("咦，怎么只有图片呀，你倒是说明一下呀，哼~"))


@add_log.got("images", prompt="图呢？")
async def add_log_got_images(bot: Bot, event: MessageEvent, state: T_State):
    images = state["images"]
    if isinstance(images, str):
        images = GetMessage(Message(images)).images
    if images:
        names = state["users"] or state["user_info"]['姓名']
        async with AddScoreLog(state["user_info"]["班级"], names, event.user_id,
                               state["user_info"]["学号"], images, state["msg"]) as res:
            await add_log.finish(res.text())
    else:
        await add_log.finish("不给图就不给加！(☆-ｖ-)")


@export_log.handle()
async def export_log_handle(bot: Bot, event: GroupMessageEvent, state: T_State):
    if await CLASS_CADRE(bot, event, state):
        async with SaveDialog(state["class_cadre"]["班级"], get_names(event.get_plaintext())) as res:
            if res.not_value:
                await export_log.finish(res.text())
            else:
                await bot.call_api("upload_group_file", group_id=event.group_id, file=res.file_path, name=res.name)


@export_prove.handle()
async def export_prove_handle(bot: Bot, event: GroupMessageEvent, state: T_State):
    if await CLASS_CADRE(bot, event, state):
        async with ExportProve(state["class_cadre"]["班级"], get_names(event.get_plaintext())) as res:
            if res.not_value:
                await export_prove.finish(res.text())
            else:
                for i in res.zip():
                    await export_prove.send(i)
                await bot.call_api("upload_group_file", group_id=event.group_id, file=res.file_path, name=res.name)

