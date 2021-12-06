from nonebot import require
from nonebot.adapters.cqhttp import Message
from asyncio import sleep
from pandas import DataFrame

from .config import Config

mysql = require("botdb").MySQLdbMethods()
config = Config()


class UserName:
    def __init__(self, users: list):
        self.users = users
        self.reply = ""
        self.sleep = 5

    async def select_user(self):
        await mysql.execute(f"select * from {config.user_table} where qq in({','.join(['%s'] * len(self.users))})",
                            self.users)
        return mysql.form()

    async def __aenter__(self):
        self.all_user: DataFrame = await self.select_user()
        return self

    def load_text(self):
        return Message(f"请稍等，预计需要{self.all_user.shape[0] * self.sleep}秒完成！")

    async def reset_name(self, group_id: int, func):
        for index, user in self.all_user.iterrows():
            await sleep(self.sleep)
            # print(f"{user['姓名']} {user['寝室']} {user['联系方式']}")
            await func(group_id=group_id, user_id=user["QQ"], card=f"{user['姓名']} {user['寝室']} {user['联系方式']}")
        self.reply = "重命名成功"

    def text(self):
        return Message(self.reply)

    async def __aexit__(self, *args):
        ...
