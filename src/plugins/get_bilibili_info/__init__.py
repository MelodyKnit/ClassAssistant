import re
from pprint import pprint

from .data_source import GetVideoInfo, GetUserInfo, get_link_redirection
from nonebot.rule import Rule, T_State
from nonebot import on_regex, on_command, on_message
from nonebot.adapters.cqhttp import Bot, MessageEvent, Event

bv_av = r"[ab]v\w+"


""" ====== rule ====== """


def is_bili_id() -> Rule:
    """
    读取消息是否包含有av或bv号，或者存在bili的xml卡片
    判断是否是消息事件，循环判断消息内是否存在xml如果不是xml将作为纯文本读取
    :return: Rule
    """
    async def _bili_xml(bot: Bot, event: Event, state: T_State) -> bool:
        if event.get_type() == "message":
            event: MessageEvent
            for msg in event.message:
                if msg.type == "xml" or msg.type == "json":
                    pprint(msg.data["data"][0])
                    text = re.search(r"https://b23.tv/\w+", str(msg.data["data"]).replace("\\", ""), re.I)
                    if text:
                        state["xml_url"] = await get_link_redirection(text.group())
                        return True
                else:
                    text = re.search(bv_av, event.get_plaintext(), flags=re.I)
                    if text:
                        state["xml_url"] = text.group()
                        return True
        return False
    return Rule(_bili_xml)


""" ====== matcher ====== """


user_info = on_command("mid", aliases={"UP", "up", "https://space.bilibili.com/"})
video_msg = on_message(rule=is_bili_id())


@video_msg.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State):
    xml_url = state.get("xml_url")
    text = re.search(bv_av, xml_url, flags=re.I)
    if text:
        async with GetVideoInfo(text.group()) as res:
            await video_msg.finish(res.text())
    elif re.search(r"space.bilibili.com/\d+", xml_url):
        # 处理用户的xml卡片
        async with GetUserInfo(re.search(r"\d+", xml_url).group()) as res:
            await user_info.finish(res.text())


@user_info.handle()
async def _(bot: Bot, event: MessageEvent):
    text = event.get_plaintext()
    if text:
        async with GetUserInfo(text) as res:
            await user_info.finish(res.text())







