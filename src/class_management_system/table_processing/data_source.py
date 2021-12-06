from datetime import datetime, timedelta
from pprint import pprint
from typing import Union
from pandas import DataFrame, Series, merge, concat
from .config import Config
from nonebot import require
from nonebot.adapters.cqhttp import Message

config = Config()
mysql = require("botdb").MySQLdbMethods()
tools = require("tools")
re_docs = tools.re_docs
get_url = tools.get_url
GetDocsSheet = tools.GetDocsSheet


class GetExcelNotUser:
    def __init__(self, class_name: str, url: str):
        self.url = url
        self.class_name = class_name
        self.reply = None

    async def select_user(self) -> DataFrame:
        await mysql.execute(f"select 姓名, QQ from {config.user_table} where 班级=%s",
                            [self.class_name])
        return mysql.form()

    async def get_sheet(self) -> DataFrame:
        try:
            async with GetDocsSheet(self.url) as res:
                return res.data
        except IndexError:
            self.reply = "查询失败，似乎表格没有设置成“所有人可编辑”请检查表格分享设置，或者重新分享一次！！"

    async def __aenter__(self):
        self.sheet = await self.get_sheet()
        self.users = await self.select_user()
        return self

    async def get_names(self):
        names = self.sheet.get("姓名")
        if not names:
            names = self.sheet.get("学生姓名")
        return names

    def text(self):
        if self.reply:
            return Message(self.reply)
        user = set(self.users.get("姓名")) - set(self.sheet.get("姓名"))
        if user:
            reply = ["未填写名单"]
            for name in user:
                reply.append(name)
            reply = ' '.join(reply)
        else:
            reply = "未发现成员！！！"
        return Message(reply)

    async def __aexit__(self, *args):
        ...


class CheckUser(GetExcelNotUser):
    async def __aenter__(self):
        self.sheet = await self.get_sheet()
        self.users = await self.select_user()
        self.columns = self.get_column()
        self.sheet = self.sheet[self.columns].astype("str")
        self.users = self.users[self.columns].astype("str")
        self.select_info()
        self.reply: DataFrame
        return self

    def super_select_info(self):
        """
        对班级进行超级校对，只要与班级信息相关的
        """
        mer = merge(self.users, self.sheet, how="inner")
        err = concat([mer, self.users], join="inner", axis=0).drop_duplicates(keep=False)
        self.reply = err
        return err

    def deep_select_info(self):
        """
        校对班级用户
        校对班级用户并且包括不在表格内的
        """
        mer = self.get_class()
        err = merge(mer, self.users, how="inner")
        err = concat([self.users, err], join="inner", axis=0).drop_duplicates(keep=False)
        self.reply = err
        return err

    def get_class(self):
        c = self.sheet.get("班级")
        if c is not None:
            return self.sheet[c == self.class_name]
        return self.sheet

    def select_info(self):
        """
        校对用户
        查询检查班级用户，并且是表格中有的
        """
        mer = self.get_class()
        err = merge(mer, self.users, how="inner")
        err = concat([mer, err], join="inner", axis=0).drop_duplicates(keep=False)
        self.reply = err
        return err

    def get_column(self) -> list:
        return list(set(self.sheet.columns) & set(self.users.columns))

    async def select_user(self) -> DataFrame:
        await mysql.execute(f"select 姓名,班级,联系方式,身份证号,qq,学号,民族,籍贯 from {config.user_table} where 班级=%s",
                            [self.class_name])
        return mysql.form()

    def text(self) -> Message:
        text = self.reply
        if text.shape[0]:
            return Message(str(text))
        return Message("未发现错误！")
