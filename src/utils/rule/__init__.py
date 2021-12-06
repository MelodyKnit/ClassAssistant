from nonebot import require, export
from nonebot.exception import FinishedException
from pandas import DataFrame
from nonebot.rule import T_State, Rule
from .config import Config
from nonebot.adapters.cqhttp import Bot, Event, GroupMessageEvent, MessageEvent

MySQLdbMethods = require("botdb").MySQLdbMethods
mysql = MySQLdbMethods()
config = Config()
export = export()


# 是否为班主任
async def _master(bot: Bot, event: Event, state: T_State, is_raise: bool = True):
    """分析是否是班主任"""
    if event.get_type() == "message":
        event: GroupMessageEvent
        await mysql.execute("select class_group, class_name from class_table where class_teacher=%s" % event.user_id)
        data = mysql.form()
        state["all_group"] = {
            "class_group": list(data["class_group"]),
            "class_name": list(data["class_name"])
        }
        if event.group_id in state["all_group"]["class_group"]:
            return True
    if is_raise:
        raise FinishedException
    return False


# 是否为班干部
async def _class_cadre(bot: Bot, event: Event, state: T_State, is_raise: bool = True):
    """
    分析是否为班干部
    会返回用户的姓名，班级，职位到state内
    """
    if event.get_type() == "message":
        event: MessageEvent
        await mysql.execute("select 姓名, 职位, 班级 from user_info where qq=%s" % event.user_id)
        data = mysql.form()
        if data.shape[0]:
            state["class_cadre"] = data.loc[0]
            if state["class_cadre"]["职位"] in config.class_cadre:
                return True
    if is_raise:
        raise FinishedException
    return False


# 是否为学生
async def _is_user(bot: Bot, event: Event, state: T_State, is_raise: bool = True):
    """
    分析是否为班级学生，并且返回学生信息（姓名，职位，班级，学号）
    """
    event_type = event.get_type()
    if event_type == "message" or event_type == "request":
        event: MessageEvent
        await mysql.execute("select 姓名, 职位, 班级, 学号, 分数 from user_info where qq=%s" % event.user_id)
        data: DataFrame = mysql.form()
        if data.shape[0]:
            state["user_info"] = data.loc[0]
            return True
    if is_raise:
        raise FinishedException
    return False


# 是否为班级群
async def _class_group(bot: Bot, event: Event, state: T_State, is_raise: bool = True):
    event_type = event.get_type()
    if event_type == "message":
        event: GroupMessageEvent
        await mysql.execute("select * from class_table where class_group=%s", [event.group_id])
        data: DataFrame = mysql.form()
        if data.shape[0]:
            state["class_group"] = data.loc[0]
            return True
    if is_raise:
        raise FinishedException
    return False


# 是否为寝室长
async def _dorm_admin(bot: Bot, event: Event, state: T_State, is_raise: bool = True):
    event_type = event.get_type()
    if event_type == "message":
        event: GroupMessageEvent
        await mysql.execute("select * from user_info where 寝室长='是' and qq=%s", [event.user_id])
        data: DataFrame = mysql.form()
        if data.shape[0]:
            state["dorm_admin"] = data.loc[0]
            return True
    if is_raise:
        raise FinishedException
    return False


export.DORM_ADMIN = Rule(_dorm_admin)
export.MASTER = Rule(_master)
export.CLASS_GROUP = Rule(_class_group)
export.IS_USER = Rule(_is_user)
export.CLASS_CADRE = Rule(_class_cadre)
export.cadres = config.class_cadre

