from datetime import datetime
from nonebot import require
from nonebot.adapters.cqhttp import Message, MessageSegment
from pandas import DataFrame
from .config import Config

mysql = require("botdb").MySQLdbMethods()
config = Config()


class SelectBirthdayUser:
    def __init__(self):
        self.now = datetime.now()
        self.month = self.now.month
        self.day = self.now.day
        self.class_user = dict()
        self.reply = ""

    async def birthday_user(self) -> DataFrame:
        """获取生日的用户"""
        await mysql.execute(f"select 姓名,qq,班级,出生日期,class_group 群号 from {config.user_table},{config.class_table} "
                            f"where month(出生日期)=%s and day(出生日期)=%s and class_name=班级",
                            [self.month, self.day])
        return mysql.form()

    async def __aenter__(self):
        self.all_user = await self.birthday_user()
        self.all_class = set(self.all_user["群号"])
        for i in self.all_class:
            self.class_user[i] = self.all_user[self.all_user["群号"] == i].reset_index().drop("index", axis=1)
        return self

    def text(self):
        for group_id in self.class_user:
            for txt in [
                "咚咚咚，还有人嘛 (′▽`〃)。",
                f"今天是{self.now.date()}，然后呢人家想悄悄告你们一个小秘密 (/▽＼)",
                f"今天是”{','.join(list(self.class_user[group_id]['姓名']))}“"
                f"同学的生日噢 (✧◡✧)！\n\n好啦好啦！你知道的太多了啦，接下来该做什么人家也不用多说了吧。 (>▽<) 嘻嘻~"
            ]:
                yield txt, group_id

    async def __aexit__(self, *args):
        ...
