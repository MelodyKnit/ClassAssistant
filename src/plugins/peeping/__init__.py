from nonebot import on_command
from nonebot.adapters.cqhttp import Bot, GroupMessageEvent, MessageSegment
from nonebot.permission import SUPERUSER
from .data_source import Peeping
from json import dumps

peeping = on_command("窥屏", permission=SUPERUSER, block=False, priority=1)


@peeping.handle()
async def peeping_handle(bot: Bot, event: GroupMessageEvent):
    async with Peeping() as res:
        await peeping.send(MessageSegment.xml(res.get_xml()))
        await peeping.finish(await res.get_send_msg())
