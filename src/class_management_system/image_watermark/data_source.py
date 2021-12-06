from nonebot import require
from io import BytesIO
from nonebot.adapters.cqhttp import MessageSegment
from PIL.PngImagePlugin import PngImageFile
from pandas import DataFrame

Watermark = require("tools").Watermark


class SetWatermark:
    def __init__(self, file, user_info: DataFrame):
        self.file = file
        self.user_info = user_info

    def image(self):
        """发送图片"""
        img_bytes = BytesIO()
        self.img.save(img_bytes, format="JPEG")
        return MessageSegment.image(img_bytes)

    async def draw(self) -> PngImageFile:
        """绘制"""
        async with Watermark(
                url=self.file,
                text=f'{self.user_info["姓名"]}\n{self.user_info["班级"]}',
                size=100,
                xy=(50, 50)) as res:
            return res.img

    async def __aenter__(self):
        self.img = await self.draw()
        return self

    async def __aexit__(self, *args):
        ...
