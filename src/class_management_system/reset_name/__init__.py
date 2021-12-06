from pprint import pprint

from nonebot import on_command, require
from nonebot.adapters.cqhttp import Bot, GroupMessageEvent
from .data_source import UserName


reset_name = on_command("重命名", aliases={"班级重命名", "学生重命名", "自动改备注"})
IS_USER = require("rule").IS_USER


def get_group_user_id(users: list):
    return [int(user["user_id"]) for user in users]


@reset_name.handle()
async def reset_name_handle(bot: Bot, event: GroupMessageEvent, state: dict):
    if await IS_USER(bot, event, state):
        group_user = get_group_user_id(await bot.get_group_member_list(group_id=event.group_id))
        async with UserName(group_user) as res:
            await reset_name.send(res.load_text())
            await res.reset_name(event.group_id, bot.set_group_card)
            await reset_name.finish(res.text())
