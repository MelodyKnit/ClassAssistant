from nonebot import require, export
from nonebot.permission import Permission, SUPERUSER
from nonebot.adapters.cqhttp import Bot, Event, MessageEvent

MySQLdbMethods = require("botdb").MySQLdbMethods
mysql = MySQLdbMethods()
export = export()


async def _teacher(bot: Bot, event: Event):
    """分析是否为教师或超级用户，如果是则满足条件"""
    if event.get_type() == "message":
        event: MessageEvent
        user_id = event.get_user_id()
        # 是否为超级用户
        if user_id in bot.config.superusers:
            return True
        else:
            # 是否为教师
            await mysql.execute("select qq from teacher where qq=%s" % event.user_id)
            return event.user_id in set(mysql.form()["qq"])
    return False


async def _class_group(bot: Bot, event: Event):
    if event.get_type() == "message":
        event: MessageEvent
        user_id = event.get_user_id()
        # 是否为超级用户
        if user_id in bot.config.superusers:
            return True
        else:
            await mysql.execute("select qq from user_info union select qq from teacher")
            return event.user_id in set(mysql.form()["qq"])
    return False

CLASS_GROUP = Permission(_class_group)
TEACHER = Permission(_teacher)
export.CLASS_GROUP = CLASS_GROUP
export.TEACHER = TEACHER
