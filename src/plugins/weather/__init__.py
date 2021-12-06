from nonebot import require, on_command, get_bot, get_driver
from .data_source import GetCurrentWeather, config, ToDayWeather
from asyncio import sleep
from nonebot.adapters.cqhttp import Bot, MessageEvent

weather = on_command("天气")
scheduler = require("nonebot_plugin_apscheduler").scheduler


@weather.handle()
async def _(bot: Bot, event: MessageEvent):
    if not config.loading_weather:
        await weather.send("正在获取当前天气，请稍后...")
        async with GetCurrentWeather() as res:
            await weather.finish(res.text())
    else:
        await weather.finish("请勿重复请求天气！")


async def today_weather(bot=None):
    bot: Bot = get_bot()
    async with ToDayWeather() as res:
        text = list(res.text())
        # for group_id in await res.get_class():
        # for msg in text:
        #     await sleep(1)
        #     await bot.send_group_msg(group_id=, message=msg)

# get_driver().on_bot_connect(today_weather)

scheduler.add_job(today_weather, 'cron', hour=6, minute=0, id='today_weather')
