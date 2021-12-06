from nonebot import require, on_command
from nonebot.adapters.cqhttp import Bot, MessageEvent
from .data_source import SetWatermark


watermark = on_command("水印", aliases={"打水印", "添加水印"})
IS_USER = require("rule").IS_USER


@watermark.handle()
async def watermark_handler(bot: Bot, event: MessageEvent, state: dict):
    if await IS_USER(bot, event, state):
        for msg in event.message:
            if msg.type == "image":
                state['params'] = True
                break


@watermark.got("params", prompt="请发送图片")
async def watermark_got(bot: Bot, event: MessageEvent, state: dict):
    for msg in event.message:
        if msg.type == "image":
            async with SetWatermark(msg.data["url"], state["user_info"]) as res:
                await watermark.send(res.image())
