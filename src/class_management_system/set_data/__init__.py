import re
from nonebot import on_command, require
from nonebot.rule import T_State
from .data_source import ADD, DEL, Faculty, Expertise, Teacher, Class
from nonebot.adapters.cqhttp import Bot, MessageEvent, GroupMessageEvent, Message
permission = require("permission")
rule = require("rule")

TEACHER = permission.TEACHER
MASTER = rule.MASTER


def teacher(matcher):
    @matcher.handle()
    async def _(bot: Bot, event: MessageEvent, state: T_State):
        # 超级用户与教师才可执行
        if await TEACHER(Bot, event):
            text = get_text(event.message)
            if text:
                state["param"] = text
        else:
            await matcher.finish()


def master(matcher):
    @matcher.handle()
    async def _(bot: Bot, event: GroupMessageEvent, state: T_State):
        # 超级用户与教师才可执行
        if await MASTER(Bot, event, state):
            state["param"] = get_text(event.message) or str(event.group_id)
        else:
            await matcher.finish()


def get_text(message: Message):
    """获取文本"""
    for msg in message:
        if msg.type == "text":
            return msg.data.get("text").strip()


# -------------------- 添加数据 --------------------
add_faculty = on_command("添加院系", aliases={"新增院系", "添加学院", "新增学院"})
add_expertise = on_command("添加专业", aliases={"新增专业"})
add_teacher = on_command("添加教师", aliases={"新增教师"})
add_class = on_command("添加班级", aliases={"新增班级"})
teacher(add_faculty)
teacher(add_expertise)
teacher(add_teacher)
teacher(add_class)


# -------------------- 删除数据 --------------------
del_faculty = on_command("删除院系", aliases={"移除院系", "剔除院系"})
del_expertise = on_command("删除专业", aliases={"移除专业", "剔除专业"})
del_teacher = on_command("删除教师", aliases={"移除教师", "剔除教师"})
del_class = on_command("删除班级", aliases={"移除班级", "剔除班级"})
teacher(del_faculty)
teacher(del_expertise)
teacher(del_teacher)
master(del_class)


# -------------------- 院系 --------------------
@add_faculty.got("param", prompt="您需要”添加“的院系名称（例如：回复信息工程, 电气工程等等...）")
async def add_faculty_got(bot: Bot, event: MessageEvent):
    text = get_text(event.message)
    if text:
        async with Faculty(ADD, text, event.user_id) as res:
            await add_faculty.finish(res.text())


# 删除
@del_faculty.got("param", prompt="您需要”删除“的院系名称（例如：回复信息工程, 电气工程等等...）")
async def add_faculty_got(bot: Bot, event: MessageEvent):
    text = get_text(event.message)
    if text:
        async with Faculty(DEL, text, event.user_id) as res:
            await del_faculty.finish(res.text())


# -------------------- 专业 --------------------
@add_expertise.got("param", prompt="您需要”添加“的专业名称（例如：回复人工智能, 服装设计等等...）")
async def add_expertise_got(bot: Bot, event: MessageEvent, state: T_State):
    state["param"] = get_text(event.message)
    if state["param"]:
        await add_expertise.send("请输入这个专业所在的院系。")
    else:
        await add_expertise.finish(Message("请认真填写内容！！！"))


@add_expertise.got("faculty")
async def expertise_in_faculty(bot: Bot, event: MessageEvent, state: T_State):
    """
    param       为专业名称
    faculty     为该专业所在院系
    """
    state["faculty"] = get_text(event.message)
    if state["param"] and state["faculty"]:
        async with Expertise(ADD, state["param"], state["faculty"]) as res:
            await add_expertise.finish(res.text())
    else:
        await add_expertise.finish(Message("请认真填写内容！！！"))


# 删除
@del_expertise.got("param", prompt="您需要”删除“的专业名称（例如：回复人工智能, 服装设计等等...）")
async def del_expertise_got(bot: Bot, event: MessageEvent, state: T_State):
    if state["param"]:
        async with Expertise(DEL, state["param"]) as res:
            await del_expertise.finish(res.text())


# -------------------- 教师 --------------------
@add_teacher.got("param", prompt="请输入您需要添加的教师的姓名")
async def add_teacher_got(bot: Bot, event: MessageEvent, state: T_State):
    state["param"] = get_text(event.message)
    if state["param"]:
        await add_teacher.send("请输入这位教师的QQ")
    else:
        await add_teacher.finish(Message("请认真填写内容！！！"))


@add_teacher.got("qq")
async def add_teacher_qq_got(bot: Bot, event: MessageEvent, state: T_State):
    state["qq"] = get_text(event.message)
    if state["qq"]:
        await add_teacher.send("请输入这位教师的手机号")
    else:
        await add_teacher.finish(Message("请认真填写内容！！！"))


@add_teacher.got("tel")
async def add_teacher_tel_got(bot: Bot, event: MessageEvent, state: T_State):
    state["tel"] = get_text(event.message)
    if state["tel"]:
        async with Teacher(ADD, state["param"], state["qq"], state["tel"], event.user_id) as res:
            await add_teacher.finish(res.text())
    else:
        await add_teacher.finish(Message("请认真填写内容！！！"))


# 删除
@del_teacher.got("param", prompt="请输入这位教师的QQ号或姓名")
async def del_teacher_got(bot: Bot, event: MessageEvent, state: T_State):
    if state["param"]:
        is_name = "name"
        if state["param"].isdigit():
            is_name = "qq"
        async with Teacher(DEL, **{is_name: state["param"]}) as res:
            await del_teacher.finish(res.text())
    else:
        await add_teacher.finish(Message("请认真填写内容！！！"))


# -------------------- 班级 ---------------------
@add_class.got("param", prompt="请输入班级名称，（例如：人工智能2101等等...）如果您在此群使用该命令，此群将会变为班级群，并且您会被认定为此群班主任，请认真确定！！！")
async def add_class_got(bot: Bot, event: GroupMessageEvent, state: T_State):
    class_name = state["param"]
    if class_name:
        split = re.findall(r"\S[^\d]+|\d+", class_name)[:2]
        if len(class_name) > 1:
            expertise, class_id = split
            if expertise.isdigit():
                expertise, class_id = class_id, class_name
            # 参数较多就这样写了
            async with Class(ADD,
                             class_name=class_name,
                             class_id=class_id,
                             class_group=event.group_id,
                             class_teacher=event.user_id,
                             expertise=expertise) as res:
                await add_class.finish(res.text())
        else:
            await add_class.finish("您缺少重要参数，您输入的班级必须包含班级名称+班级号，例如：人工智能2101等等...")
    else:
        await add_teacher.finish(Message("请认真填写内容！！！"))


# 删除
@del_class.got("param", prompt="请输入班级名称或群号")
async def del_class_got(bot: Bot, event: GroupMessageEvent, state: T_State):
    is_admin = True
    state["del_type"] = "class_group"
    if state["param"]:
        if state["param"].isdigit():
            state["class_group"] = int(state["param"])
            is_admin = state["class_group"] in state["all_group"]["class_group"]
        else:
            state["del_type"] = "class_name"
            state["class_group"] = state["param"]
            is_admin = state["class_group"] in state["all_group"]["class_name"]
    else:
        state["class_group"] = event.group_id
    if not is_admin:
        await del_class.finish(Message("您并不是班主任，无权操作此群！！！"))
    await del_class.send(Message(f"您确认要将“{state['class_group']}”从班级管理系统中永久删除吗？（是/否）"))


@del_class.got("is_del")
async def del_class_is_got(bot: Bot, event: GroupMessageEvent, state: T_State):
    if "是" in state["is_del"]:
        async with Class(DEL, **{state["del_type"]: state["class_group"]}) as res:
            await del_class.finish(res.text())
    else:
        await del_class.finish("已为您取消。")


