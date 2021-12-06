from pandas import DataFrame
from aiohttp import ClientSession
from datetime import datetime, timedelta
import re

from typing import List

docs_url = "https://docs.qq.com/dop-api/opendoc"
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/94.0.4606.61 Safari/537.36 ",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "appName": "Opera"
}


class GetDocsSheet:

    def __init__(self, url: str):
        self.url = url
        self.session = ClientSession()

    @property
    def params(self):
        """提取URL所需params"""
        params = {
            "outformat": 1,
            "normal": 1
        }
        url = self.url.split("/")[-1]
        param = re.findall(r"^\w+|tab=\w+", url)
        params["id"] = param[0]
        if len(param) > 1:
            params["tab"] = param[1].replace("tab=", "")
        return params

    async def get(self):
        async with self.session.get(docs_url, headers=headers, params=self.params) as res:
            return await res.json()

    @staticmethod
    def extract(data: dict):
        for values in data["clientVars"]["collab_client_vars"]["initialAttributedText"]["text"][0]:
            for value in values:
                if isinstance(value["c"][1], dict):
                    for i in value:
                        if isinstance(value[i], list):
                            return value[i]

    def convert2d(self) -> list:
        """
        转换未二维列表

        从列表第一位开始取，按照长度推算出后面内容的序号
        然后按照序号去循环，推导出内容
            如果序号存在就查看序号内是否有值，取出值
            不存在则全部替换为空
        """
        data = []
        keys = list(self.raw_data.keys())
        length = len(keys)
        index = 0
        while index < length:
            key = int(keys[index])
            if not key % self.columns:
                arr = []
                for key in range(key, key + self.columns):
                    values = self.raw_data.get(str(key))
                    if values:
                        index += 1
                        value = values.get("2")
                        arr.append(value[1] if value else value)
                        continue
                    arr.append(values)
                data.append(arr)
            else:
                index += 1
        return data

    def data_frame(self):
        """
        找出columns所在位置
        """
        # 清除空行空列
        df = DataFrame(self.convert2d(), dtype="str").dropna(axis=0, how='all').dropna(axis=1, how='all')
        for i, v in enumerate(df.values):
            if all(v):
                return DataFrame(df.values[i+1:], columns=list(v))

    async def __aenter__(self):
        data = self.extract(await self.get())
        self.columns = data[0][-1] + 1
        self.rows = data[0][-3] + 1
        self.raw_data = data[1]
        self.data = self.data_frame()
        return self

    @staticmethod
    def get_excel_date(date_int: int):
        """对于excel日期进行转换，以便写入数据"""
        if date_int:
            return str((datetime(1899, 12, 30) + timedelta(int(date_int) + 1)).date())
        return None

    def reset_date(self, typeof: str = "出生日期"):
        """重置表格日期表格"""
        try:
            self.data[typeof] = [self.get_excel_date(i) for i in self.data[typeof]]
        except IndexError:
            ...
        finally:
            return self

    async def __aexit__(self, *args):
        await self.session.close()


class QueryUser:
    def __init__(self, params: List[str], class_name: str = None, group_id: int = None):
        if not(class_name or group_id):
            raise "Missing required parameters class_name or group_id"
        self.params = params
        self.class_name = class_name
        self.group_id = group_id
        self.index = []
        self.name = []
        self.user_id = []

    def split_param(self):
        """
        拆分参数
        字符串作为名字传入 name
        如果是数字判断数字是序号还是id
        满足长度四位的为序号
        超过的为id
        """
        for i in self.params:
            if i.isdigit():
                i = int(i)
                if i < 1000:
                    self.index.append(i)
                else:
                    self.user_id.append(i)
            else:
                self.name.append(i)

    async def __aenter__(self):
        ...

    async def __aexit__(self, *args):
        ...
