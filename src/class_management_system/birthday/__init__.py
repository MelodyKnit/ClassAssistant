from pprint import pprint

from nonebot import require, get_driver, get_bot
from asyncio import sleep
from nonebot.adapters.cqhttp import Bot, Message
from .data_source import config, SelectBirthdayUser

driver = get_driver()
scheduler = require("nonebot_plugin_apscheduler").scheduler


async def birthday(bot: Bot):
    async with SelectBirthdayUser() as res:
        for txt, group_id in res.text():
            await sleep(5)
            await bot.send_group_msg(group_id=group_id, message=txt)


@driver.on_bot_connect
async def _(bot: Bot):
    scheduler.add_job(birthday, 'cron', hour=0, minute=0, id='birthday', args=[bot])
