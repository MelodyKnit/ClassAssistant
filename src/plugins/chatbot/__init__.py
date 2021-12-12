from nonebot import on_command, on_message
from nonebot.permission import SUPERUSER
from nonebot.rule import T_State
from nonebot.adapters.cqhttp import Bot, MessageEvent, GroupMessageEvent
from .config import Config
from .data_source import AddChatWord, get_url, BotChat


# export_chat = on_command("导入词库", aliases={"添加词库", "更新词库"})
on_chat = on_message(priority=100)
chat_ends = ["再见", "不聊了", "结束对话", "拜拜", "bye"]


# @export_chat.handle()
# async def export_chat_handle(bot: Bot, event: MessageEvent, state: T_State):
#     if await SUPERUSER(bot, event):
#         url = get_url(event.message)
#         if url:
#             state["url"] = url
#     else:
#         await export_chat.finish()
#
#
# @export_chat.got("url", prompt="请发送在线文档链接或卡片")
# async def export_chat_got(bot: Bot, event: MessageEvent, state: T_State):
#     url = get_url(state["url"])
#     if url:
#         async with AddChatWord(url) as res:
#             await export_chat.finish(res.text())
#     else:
#         await export_chat.finish("添加失败！！！")


@on_chat.handle()
async def on_chat_handle(bot: Bot, event: MessageEvent, state: T_State):
    if event.to_me:
        state["start"] = "开始聊天"
    else:
        await on_chat.finish()


@on_chat.got("start")
async def on_chat_got(bot: Bot, event: MessageEvent):
    text = event.get_plaintext()
    if text:
        for txt in chat_ends:
            if txt in text:
                await on_chat.finish("拜拜！")
        async with BotChat(text) as res:
            if isinstance(event, GroupMessageEvent):
                await on_chat.reject(await res.text())
            await on_chat.finish(await res.text())

