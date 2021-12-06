from nonebot import get_driver, on_command
from aiohttp import ClientSession
from nonebot.adapters.cqhttp import Bot, MessageEvent, Message
from nonebot.rule import T_State
from .config import Config

covid = on_command("疫情", aliases={"疫情查询"})
get_covid = []


@covid.handle()
async def covid_handler(bot: Bot, event: MessageEvent, state: T_State):
    text = event.get_plaintext()
    if text and event.user_id not in get_covid:
        state["region"] = text
        get_covid.append(event.user_id)
    else:
        await covid.finish("请勿频繁获取！！！")


@covid.got("region", prompt="请发送地区")
async def covid_got(bot: Bot, event: MessageEvent, state: T_State):
    text = state["region"]
    await covid.send(Message("正在获取中..."))
    try:
        async with ClientSession() as session:
            async with session.get("https://api.iyk0.com/yq/", params={"msg": text}) as res:
                data = await res.json()
                if data["code"] == 200:
                    await covid.send(Message(f'{data["msg"]}\n'
                                             f'查询地区：{data["查询地区"]}\n'
                                             f'目前确诊：{data["目前确诊"]}\n'
                                             f'死亡人数：{data["死亡人数"]}\n'
                                             f'治愈人数：{data["治愈人数"]}\n'
                                             f'新增确诊：{data["新增确诊"]}\n'
                                             f'现存无症状：{data["现存无症状"]}\n'
                                             f'更新时间：{data["time"]}'))
                elif data["code"] == 202:
                    await covid.send(Message(data["msg"]))
    finally:
        get_covid.remove(event.user_id)
