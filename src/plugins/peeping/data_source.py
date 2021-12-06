from pprint import pprint

from aiohttp import ClientSession
from asyncio import sleep
from json import loads
from typing import Union, List
from json import dumps

main_url = "http://melodyknit.club:8000/peeping"

xml = """<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><msg serviceID="1" templateID="12345" action="web" brief="这个视频很nb" sourceMsgId="0" url="https://b23.tv/T4eA6C" flag="0" adverSign="0" multiMsgFlag="0"><item layout="2" advertiser_id="0" aid="0"><picture cover="{url}" w="0" h="0" /><title>我爱死这个视频了</title><summary>这简直是视觉盛宴！！！</summary></item><source name="" icon="" action="" appid="0" /></msg>"""


class Peeping:
    card = {
        "app": "com.tencent.structmsg",
        "config": {
            "autosize": True,
            "ctime": 1636171890,
            "forward": True,
            "token": "7264596b2c6ae2063f045293b78db1dc",
            "type": "normal"
        },
        "desc": "新闻",
        "extra": {
            "app_type": 1,
            "appid": 100951776,
            "msg_seq": 7027304746066715522,
            "uin": 2711402357
        },
        "meta": {
            "news": {
                "action": "",
                "android_pkg_name": "",
                "app_type": 1,
                "appid": 100951776,
                "desc": "你感兴趣的视频都在B站",
                "jumpUrl": "https://b23.tv/mGMAnD?share_medium=android&share_source=qq&bbid=XX5AE4A57C36D652CA32EB08BA6E8735D8FDF&ts=1636171884331",
                "preview": "https://open.gtimg.cn/open/app_icon/00/95/17/76/100951776_100_m.png?t=1635933215?date=20211106",
                "source_icon": "",
                "source_url": "",
                "tag": "哔哩哔哩",
                "title": "MelodyKnit的个人空间"
            }
        },
        "prompt": "[分享]MelodyKnit的个人空间",
        "ver": "0.0.0.1",
        "view": "news"
    }

    def __init__(self, interval: int = 5):
        self._xml = xml
        self._session = ClientSession()
        self.uid = None
        self.interval = interval
        self.img_url = f"{main_url}/image?uid="

    async def _get(self, url, params=None) -> Union[dict, list]:
        async with self._session.get(url, params=params) as res:
            return loads(await res.read())

    async def __aenter__(self):
        self.uid = (await self._get(main_url))["uid"]
        self.img_url += str(self.uid)
        return self

    def get_xml(self) -> str:
        return self._xml.format(url=self.img_url)

    def get_json(self):
        # self.card["meta"]["news"]["source_icon"] = self.img_url
        return dumps(self.card)

    @staticmethod
    def _msg(info) -> str:
        return (f"时间：{info['time']}\n"
                f"IP：{info['host']}\n"
                f"所在地：{info['referer']}\n"
                f"设备：{info['ua']}")

    async def get_data(self) -> List[dict]:
        await sleep(self.interval - 1)
        return await self._get(main_url, params={"uid": self.uid})

    async def get_send_msg(self) -> str:
        data = await self.get_data()
        if data:
            return "\n---\n".join([self._msg(info) for info in data])
        else:
            return "未发现"

    async def __aexit__(self, *ags):
        await self._session.close()
