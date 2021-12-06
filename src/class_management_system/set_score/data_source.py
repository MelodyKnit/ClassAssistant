from nonebot import require
from .config import Config
from nonebot.adapters.cqhttp import Message
import re

config = Config()
mysql = require("botdb").MySQLdbMethods()


class SetScore:
    def __init__(self, class_name: str, text: str):
        self.class_name = class_name
        self.params = [i.split() for i in re.findall(r"\S.*?\d+", text)]

    async def set_score(self, score: int, names: list):
        await mysql.execute_commit(f"update {config.user_table} set 分数=分数+%s "
                                   f"where 班级=%s and 姓名 in({','.join(['%s'] * len(names))})",
                                   [score, self.class_name, *names])

    async def __aenter__(self):
        if self.params:
            for param in self.params:
                await self.set_score(int(param[-1]), param[:-1])
            self.reply = "分数增改成功！"
        else:
            self.reply = "未写入加分名单！！！"
        return self

    def text(self):
        return Message(self.reply)

    async def __aexit__(self, *args):
        ...


class GiftScore:
    def __init__(self, class_name: str, user_id: int, my_score: int, to_name: str):
        self.class_name = class_name
        self.my_score = my_score
        self.user_id = user_id
        self.to_name = to_name
        self.reply = ""

    async def gift_score(self):
        await mysql.execute_commit(f"update {config.user_table} set 分数=分数+%s "
                                   f"where 班级=%s and 姓名=%s", [self.score, self.class_name, self.to_name])
        await mysql.execute_commit(f"update {config.user_table} set 分数=分数-%s "
                                   f"where 班级=%s and qq=%s", [self.score, self.class_name, self.user_id])

    async def __aenter__(self):
        self.to_name = self.to_name.split()
        if len(self.to_name) > 1:
            self.to_name, self.score = self.to_name[:2]
            if self.score.isdigit():
                self.score = int(self.score)
                if 0 < self.my_score >= self.score:
                    await self.gift_score()
                    self.reply = f"成功转让{self.score}给{self.to_name}"
                else:
                    self.reply = f"抱歉，您的分数不足{self.score}！！！"
            else:
                self.reply = "输入有误，您的第二个参数应该是纯数字！！！"
        else:
            self.reply = "输入有误，确认输入格式：姓名 数量"
        return self

    def text(self):
        return Message(self.reply)

    async def __aexit__(self, *args):
        ...
