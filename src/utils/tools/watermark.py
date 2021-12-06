from typing import Tuple, Union

from PIL import Image, ImageDraw, ImageFont
from PIL.PngImagePlugin import PngImageFile
from aiohttp import ClientSession
from io import BytesIO


class Watermark:
    def __init__(self,
                 file: Union[str, bytes] = None,
                 url: str = None,
                 text: str = None,
                 size: int = 50,
                 font: str = "simhei.ttf",
                 xy: Tuple[int, int] = None,
                 fill: Tuple[int, int, int] = None):
        self.url = url
        self.file = file
        self.text = text
        self.size = size
        self.font = font
        self.xy = xy or (0, 0)
        self.fill = fill or (255, 0, 0)

    async def url_img(self) -> PngImageFile:
        """下载图片"""
        async with ClientSession() as session:
            async with session.get(self.url) as res:
                return Image.open(BytesIO(await res.read()))

    def byte_img(self) -> PngImageFile:
        """数据流"""
        return Image.open(BytesIO(self.file))

    def local_img(self):
        """本地图片"""
        return Image.open(self.file)

    def draw(self, img: PngImageFile = None) -> PngImageFile:
        """绘制"""
        img = self.img
        draw = ImageDraw.Draw(img)
        draw.text(xy=self.xy, text=self.text, fill=self.fill,
                  font=ImageFont.truetype(font=self.font, size=self.size))
        return img

    async def __aenter__(self):
        if self.file:
            if isinstance(self.file, bytes):
                self.img = self.byte_img()
            else:
                self.img = self.local_img()
        elif self.url:
            self.img = await self.url_img()
        else:
            raise TypeError("String or Bytes")
        self.draw()
        return self

    async def __aexit__(self, *args):
        ...
