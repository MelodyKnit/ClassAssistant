from nonebot import on_request, require
from nonebot.adapters.cqhttp import Bot, FriendRequestEvent


friends = on_request()
IS_USER = require("rule").IS_USER


@friends.handle()
async def friends_handle(bot: Bot, event: FriendRequestEvent, state: dict):
    if await IS_USER(bot, event, state):
        text = f"{state['user_info']['班级']}-{state['user_info']['姓名']}"
        await bot.set_friend_add_request(flag=event.flag, approve=True, remark=text)
