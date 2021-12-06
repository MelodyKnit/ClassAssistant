from nonebot import on_command, require
from nonebot.adapters.cqhttp import Bot, GroupMessageEvent
from .query import QueryUsers

find = on_command("find")
rule = require("rule")
IS_USER = rule.IS_USER
CLASS_GROUP = rule.CLASS_GROUP
MASTER = rule.MASTER


@find.handle()
async def _(bot: Bot, event: GroupMessageEvent, state: dict):
    if await CLASS_GROUP(bot, event, state):
        search = event.get_plaintext().split("-")

        # 判断第0个是否有输入需要搜索的某位用户，如果没有就默认为自己
        if not search[0]:
            user_split = QueryUsers.split()
            user_split.user_id.append(event.user_id)
        else:
            user_split = QueryUsers.split(event.message)

            # 判断是否存在第二个值，作为搜索展示出的内容
        search = (search[1].split() if search[-1] else None) if len(search) > 1 else None

        users = QueryUsers(state["class_group"]["class_name"], search)
        await find.finish(await users.text(user_split))
