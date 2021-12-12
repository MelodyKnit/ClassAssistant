from nonebot import get_driver, on_command, on_notice
from aiohttp import ClientSession
from nonebot.adapters.cqhttp import Bot, MessageEvent, Message, PokeNotifyEvent, MessageSegment
from nonebot.rule import T_State
from .config import Config

encyclopedia = on_command("百科", aliases={"百科搜索"})
echo = on_command("echo")
get_covid = []


@echo.handle()
async def echo_handler(bot: Bot, event: MessageEvent):
    await echo.finish(event.message)


@encyclopedia.handle()
async def covid_handler(bot: Bot, event: MessageEvent, state: T_State):
    text = event.get_plaintext()
    if text and event.user_id not in get_covid:
        state["region"] = text
        get_covid.append(event.user_id)
    else:
        await encyclopedia.finish("请勿频繁获取！！！")


@encyclopedia.got("region", prompt="请发送搜索内容")
async def covid_got(bot: Bot, event: MessageEvent, state: T_State):
    text = state["region"]
    await encyclopedia.send(Message("正在获取中..."))
    try:
        async with ClientSession() as session:
            async with session.get("https://api.iyk0.com/sgbk/", params={"msg": text}) as res:
                data = await res.json()
                if data["code"] == 200:
                    await encyclopedia.send(Message(f"内容：{data['data']}\n---\n"
                                                    f"类型：{data['type']}\n---\n"
                                                    f"更多：{data['more']}"))
                elif data["code"] == 202:
                    await encyclopedia.send(Message(data["msg"]))
    finally:
        get_covid.remove(event.user_id)
