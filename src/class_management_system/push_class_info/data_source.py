from aiohttp import ClientSession
from pandas import DataFrame, Series
from datetime import datetime, timedelta
from aiomysql import IntegrityError
from nonebot import require
from nonebot.adapters.cqhttp import Message
import re
from .config import Config


config = Config()
mysql = require("botdb").MySQLdbMethods()
main_url = "https://docs.qq.com/dop-api/opendoc"
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/94.0.4606.61 Safari/537.36 ",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "appName": "Opera"
}


class Frame:
    def __init__(self, data: list):
        data = self._raw_data(data)
        self.columns = data[0][-1] + 1
        self.rows = data[0][-3] + 1
        self.raw_data = data[1]
        self.data = self._data_frame()

    def _data_frame(self):
        """提取数据"""
        df = []
        index = 0
        # 将列表转为二维
        for i in self.raw_data:
            if not int(i) % self.columns:
                df.append([])
                index += 1
            value = self.raw_data[i].get("2")
            df[index - 1].append(value[1] if value else value)
        # 清除空行空列
        df = DataFrame(df, dtype="object").dropna(axis=0, how='all').dropna(axis=1, how='all')
        index = 0
        columns = False
        # 提取columns，标题
        for i in df.values:
            index += 1
            if not all(i) and not columns:
                continue
            elif not columns:
                return DataFrame(df.values[index:], columns=list(i), dtype="object")

    @staticmethod
    def _raw_data(data):
        """解析数据，并且可以得出行列与出未加工的数据"""
        for values in data["clientVars"]["collab_client_vars"]["initialAttributedText"]["text"][0]:
            for value in values:
                if isinstance(value["c"][1], dict):
                    for i in value:
                        if isinstance(value[i], list):
                            return value[i]

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


async def get(url: str, params: dict = None) -> Frame:
    params = params or []
    async with ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as res:
            return Frame(await res.json())


class InsertUser:
    """
    写入班级信息
    """
    def __init__(self, url: str, class_name: str):
        self.url = url
        self.class_name = class_name
        self.reply = Message()

    def get_params(self) -> dict:
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

    def set_sql(self, params: Series):
        """
        从DataFrame中提取出的每一个Series
        筛选出列名，然后筛选出必填选项，也就是不能为空的参数
        :return: sql语句, sql参数（数据）
        """
        keys = set(params.keys()) & set(config.user_table_param_type.keys())
        null_param = set(config.user_table_param_not_null.keys()) - keys
        for i in keys:
            if params[i]:
                params[i] = config.user_table_param_type[i](params[i])
        if not null_param:
            sql = f"insert into {config.user_table} ({','.join([*keys, '班级'])}) value ({','.join(['%s'] * (len(keys) + 1))})"
            param = list([*params.loc[keys].values, self.class_name])
            return sql, param
        else:
            return None, null_param

    @staticmethod
    async def execute_commit(sql: str, params: list = None):
        """向数据库写入数据"""
        params = params or []
        try:
            await mysql.execute_commit(sql, params)
        except IntegrityError:
            """数据已存在"""

    async def insert(self):
        """写入数据库"""
        try:
            for i, v in enumerate(self.data.loc):     # type: Series
                sql, params = self.set_sql(v)
                if sql and params:
                    await self.execute_commit(sql, params)
                elif params:
                    self.reply.append(f"没缺少必要参数有”{','.join(params)}“并且该参数不能为空")
                    break
        except KeyError as err:
            """暂时未知的报错原因，大概原因是因为索引从0开始没有len所描述的最后一位所以报错"""
            if isinstance(err.args[0], int):
                self.reply.append("成功更新班级成员信息，可以使用查询来查看自己信息，如有错误需要修改可以使用修改命令修改本人信息！")
            else:
                self.reply.append("缺少必要参数%s，并且该参数不能为空！！！" % err)

    async def delete_user_info(self):
        print(self.class_name)
        # await mysql.execute_commit("delete from user_info where 班级=%s", [self.class_name])

    async def __aenter__(self):
        data = (await get(main_url, self.get_params())).reset_date()
        # self.class_name = await self.get_class_name()
        await self.delete_user_info()
        self.data = data.data
        await self.insert()
        return self

    def text(self):
        if isinstance(self.reply, Message):
            return self.reply
        return Message(self.reply)

    async def __aexit__(self, *args):
        ...
