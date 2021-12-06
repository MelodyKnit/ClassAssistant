from nonebot import on_command
from random import choice
from nonebot.adapters.cqhttp import Bot, MessageEvent, Message

on_random = on_command("随机")


@on_random.handle()
async def random_handle(bot: Bot, event: MessageEvent, state: dict):
    params = event.get_plaintext().split()
    if len(params) > 1:
        await on_random.finish(Message(choice(params)))

