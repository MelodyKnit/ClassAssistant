import re
from asyncio import sleep
from json import loads
from time import time
from aiohttp import ClientSession, ClientConnectionError
from nonebot.adapters.cqhttp import MessageSegment, Message
from nonebot import require
from .config import Config
from typing import Optional
from datetime import datetime

config = Config()
weather_api = Config.OppoWeatherApi
mysql = require("botdb").MySQLdbMethods()


class MessageBar(Message):
    def __getattr__(self, item):
        return lambda *args, **kwargs: self.append(getattr(MessageSegment, item)(*args, **kwargs))


class GetCurrentWeather:
    weather_api = Config.CmaWeatherApi
    """获取当时天气"""
    async def close(self):
        await self.session.close()

    def __init__(self):
        config.loading_weather = True
        self.data: Optional[dict] = None

    async def __aenter__(self):
        self.session = ClientSession()
        await self.get()
        return self

    async def get(self):
        async with self.session.get(self.weather_api.url, params=self.weather_api.params) as res:
            self.data = (await res.json())["data"]

    def precipitation(self):
        if self.data["now"]["precipitation"] >= 100:
            return 0.0
        return self.data["now"]["precipitation"]

    def text(self):
        config.loading_weather = False
        location = self.data["location"]
        now = self.data["now"]
        return (MessageBar().text(
            f"{location['name']}当前天气状况\n"
            f"温度: {now['temperature']}°C\n"
            f"湿度: {now['humidity']}%\n"
            f"降雨: {now['precipitation']}mm\n"
            f"风向: {now['windDirection']} {now['windScale']}\n"
            f"大气压: {now['pressure']}hPa\n"
            f"数据更新时间: {self.data['lastUpdate']}"
        ))

    async def __aexit__(self, *args):
        await self.session.close()


class ToDayWeather:
    url = "https://wis.qq.com/weather/common"
    direction = ["北风", "东北风", "东风", "东南风", "南风", "西南风", "西风", "西北风"]

    @property
    def params(self):
        return {
            "source": "pc",
            "weather_type": "observe|index|tips|air|forecast_24h",
            "province": "湖南省",
            "city": "长沙市",
            "county": "",
            "callback": "weather",
            "_": time()
        }

    def forecast(self):
        day = str(self.date.date())
        forecast = self.data["forecast_24h"]
        for i in forecast:
            if forecast[i]["time"] == day:
                return forecast[i]["max_degree"] + "-" + forecast[i]["min_degree"] + "°C"

    async def get(self, err_: int = 0) -> dict:
        try:
            async with ClientSession() as session:
                async with session.get(self.url, params=self.params) as res:
                    return loads(re.sub(r"^\S+\(|\)$", "", await res.text()))["data"]
        except ClientConnectionError as err:
            if err_ < 3:
                return await self.get(err_ + 1)
            else:
                raise ClientConnectionError(err)

    def suggest(self):
        """今日天气建议"""
        text = []
        index: dict = self.data.get("index")
        for i in {"sports",
                  "clothes",
                  # "comfort",
                  # "dry",
                  "makeup",
                  "morning",
                  "umbrella",
                  # "allergy",
                  "ultraviolet"
                  # "sunscreen"
                  }:
            value = index[i]["detail"] or index[i]["info"]
            if value:
                text.append(f'{index[i]["name"]}：{value}')
        return "\n- - - - - - - - - - -\n".join(text)

    def weather(self):
        """天气"""
        w = self.data["observe"]
        return (f"今天是{self.date.date()}长沙当前天气\n"
                f"天气：{w['weather']}\n"
                f"气温：{self.forecast()}\n"
                f"当前气温：{w['degree']}°C\n"
                f"气压：{w['pressure']}hPa\n"
                f"湿度：{w['humidity']}%\n"
                f"降雨率：{w['precipitation']}%\n"
                f"风向：{self.direction[int(w['wind_direction'])]} {w['wind_power']}级")

    def air(self):
        """空气质量"""
        air = self.data["air"]
        return (f"空气质量：{air['aqi']} {air['aqi_name']}\n"
                f"co：{air['co']}\n"
                f"no2：{air['no2']}\n"
                f"o3：{air['o3']}\n"
                f"pm10：{air['pm10']}\n"
                f"pm2.5：{air['pm2.5']}\n"
                f"so2：{air['so2']}"
                )

    def text(self):
        yield self.weather() + "\n- - - - - - - - - -\n" + self.air()
        yield self.suggest()

    @staticmethod
    async def get_class():
        await mysql.execute("select * from class_table")
        class_id = list(mysql.form().get("class_group"))
        return class_id or []

    async def __aenter__(self):
        self.date = datetime.now()
        self.data = await self.get()
        return self

    async def __aexit__(self, *args):
        ...
