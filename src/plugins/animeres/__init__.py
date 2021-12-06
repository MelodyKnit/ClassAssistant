from nonebot.rule import T_State
from nonebot import on_command
from nonebot.adapters.cqhttp import Bot, MessageEvent, Message
from .data_source import GetDMHY


anime_res = on_command("资源", aliases={"动漫资源"})


@anime_res.handle()
async def anime_res_handle(bot: Bot, event: MessageEvent, state: T_State):
    msg = event.get_plaintext()
    if msg:
        state["msg"] = msg


@anime_res.got("msg", prompt="动漫名字叫什么呀！")
async def anime_res_got(bot: Bot, event: MessageEvent, state: T_State):
    msg = event.get_plaintext()
    if not msg:
        await anime_res.finish("...")
    async with GetDMHY(msg) as res:
        if not res:
            await anime_res.finish("没有找到你想要的，看看是不是输错了吧！")
        state["res"] = res
        types = '\n'.join([f'{i+1}:{v}' for i, v in enumerate(res)])
        await anime_res.send(f"你需要什么类型的资源：{types}")


@anime_res.got("index")
async def anime_res_index(bot: Bot, event: MessageEvent, state: T_State):
    index = state["index"]
    if index.isdigit():
        res: GetDMHY = state["res"]
        index = int(index)
        if 0 < index <= res.length:
            anime = res[res.tags[index-1]][0]
            await anime_res.finish(f"资源名称：{anime.title}\n{anime.href}")
        else:
            await anime_res.finish("有这个序号吗？")
    else:
        await anime_res.finish("您输入的是什么呀，让你输入数字呢！")
