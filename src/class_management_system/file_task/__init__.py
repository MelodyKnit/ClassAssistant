from nonebot import on_command, require
from nonebot.adapters.cqhttp import Bot, GroupMessageEvent, MessageEvent
from .data_source import SelectTasks, AddTask, PushTaskFile, Image, ExportTask, DeleteTask

rule = require("rule")
IS_USER = rule.IS_USER
CLASS_CADRE = rule.CLASS_CADRE
query_task = on_command("查询任务")
add_task = on_command("添加任务")
push_task_file = on_command("提交任务")
export_task = on_command("导出任务")
delete_task = on_command("删除任务")


# 查询任务
@query_task.handle()
async def _(bot: Bot, event: MessageEvent, state: dict):
    if await IS_USER(bot, event, state):
        text = event.get_plaintext()
        task: SelectTasks = await SelectTasks(
            state["user_info"]["班级"],
            int(text) - 1 if text.isdigit() else None)
        async for msg in task.text():
            await query_task.send(msg)


# 添加任务
@add_task.handle()
async def _(bot: Bot, event: MessageEvent, state: dict):
    if await CLASS_CADRE(bot, event, state):
        text = event.get_plaintext()
        if text:
            state["title"] = text


@add_task.got("title", prompt="这个任务的标题叫什么呢？")
async def _(bot: Bot, event: MessageEvent, state: dict):
    text = event.get_plaintext()
    if text:
        async with AddTask(text, event.user_id, state["class_cadre"]["班级"], state["class_cadre"]["职位"]) as text:
            await add_task.finish(text)
    else:
        await add_task.finish("不告诉我就不给你添加了，哼~")


# 提交任务
@push_task_file.handle()
async def _(bot: Bot, event: MessageEvent, state: dict):
    if await IS_USER(bot, event, state):
        text = event.get_plaintext()
        task: PushTaskFile = await PushTaskFile(state["user_info"]["班级"], int(text) - 1 if text.isdigit() else None)
        state["task"] = task
        if not task:
            await push_task_file.finish(await task.text_one())
        elif task.index is None:
            await push_task_file.send(await task.text_one())
        else:
            state['index'] = task.index


@push_task_file.got("index", prompt="你想交第几个任务呀！")
async def _(bot: Bot, event: MessageEvent, state: dict):
    index = state["index"]
    task: PushTaskFile = state["task"]
    if not isinstance(index, int):
        text = event.get_plaintext()
        index = int(text) - 1 if text.isdigit() else None
    if index is None:
        await push_task_file.finish(f"不提交就算了，哼~")
    elif index not in task:
        await push_task_file.finish(f"你有看到我给你列出{index+1}号吗？哼~")

    task(state["user_info"]["姓名"], event.user_id, index)


@push_task_file.got('file', prompt="文件给我吧。")
async def _(bot: Bot, event: MessageEvent, state: dict):
    task: PushTaskFile = state["task"]
    image = [Image(msg.data) for msg in event.message if msg.type == "image"]
    if image:
        image = image[0]
        if await task.file_exists(image):
            await push_task_file.finish("你这是拿别人的文件吧，不要瞎搞哦！")
        else:
            await push_task_file.finish(await task.save(image))
    else:
        await push_task_file.finish("文件呢？")


# 导出任务
@export_task.handle()
async def _(bot: Bot, event: GroupMessageEvent, state: dict):
    if await CLASS_CADRE(bot, event, state):
        text = event.get_plaintext()
        task: ExportTask = await ExportTask(state["class_cadre"]["班级"], int(text) - 1 if text.isdigit() else None)
        state["task"] = task
        if not task:
            await export_task.finish(await task.text_one())
        elif task.index is None:
            await export_task.send(await task.text_one())
        else:
            state['index'] = task.index


@export_task.got("index", prompt="你想导出第几个任务呀！")
async def _(bot: Bot, event: GroupMessageEvent, state: dict):
    index = state["index"]
    task: ExportTask = state["task"]
    if not isinstance(index, int):
        text = event.get_plaintext()
        index = int(text) - 1 if text.isdigit() else None
    if index is None:
        await export_task.finish(f"不提交就算了，哼~")
    elif index not in task:
        await export_task.finish(f"你有看到我给你列出{index+1}号吗？哼~")

    if task(index).task_user.shape[0]:
        await export_task.send("开始进行打包咯...")
        file, name = task.zip()
        await export_task.send("打包完成，开始发送文件...")
        await bot.call_api("upload_group_file", group_id=event.group_id, file=file, name=name)
    else:
        await export_task.finish("都没人提交，你这叫我怎么导出嘛！")


# 删除任务
@delete_task.handle()
async def _(bot: Bot, event: GroupMessageEvent, state: dict):
    if await CLASS_CADRE(bot, event, state):
        text = event.get_plaintext()
        task: DeleteTask = await DeleteTask(state["class_cadre"]["班级"], int(text) - 1 if text.isdigit() else None)
        state["task"] = task
        if not task:
            await delete_task.finish(await task.text_one())
        elif task.index is None:
            await delete_task.send(await task.text_one())
        else:
            state['index'] = task.index


@delete_task.got("index", prompt="你想删除第几个任务呀！")
async def _(bot: Bot, event: MessageEvent, state: dict):
    index = state["index"]
    task: ExportTask = state["task"]
    if not isinstance(index, int):
        text = event.get_plaintext()
        index = int(text) - 1 if text.isdigit() else None
    if index is None:
        await delete_task.finish(f"取消删除")
    elif index not in task:
        await delete_task.finish(f"你有看到我给你列出{index + 1}号吗？哼~")
    state["index"] = index
    await delete_task.send(f"如果真的要删除”{task[index]['title']}“请发送”确认“。")


@delete_task.got("delete")
async def _(bot: Bot, event: MessageEvent, state: dict):
    if "确认" in event.get_plaintext():
        task: DeleteTask = state["task"](state["index"])
        await delete_task.finish(await task.delete())
