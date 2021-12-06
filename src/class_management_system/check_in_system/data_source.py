from nonebot import require
from typing import Dict

from .config import Config
from nonebot.adapters.cqhttp import Message, MessageSegment
from pandas import DataFrame, concat, Series

mysql = require("botdb").MySQLdbMethods()
config = Config()
sign_ins = {}


def reset_index(df: DataFrame) -> DataFrame:
    return df.reset_index().drop("index", axis=1)


class SetSignIn:
    def __init__(self, class_name: str, key: Message, typeof: str):
        self.class_name = class_name  # 班级名称
        self.key = key  # 签到关键字
        self.sign_users = []  # 已签到用户
        self.existence = False
        self.reply = ""
        self.typeof = typeof

    def add_sign_in(self):
        """
        添加签到
        判断班级是否有加入签到
        """
        if self.class_name not in sign_ins.keys() or self.existence:
            self.existence = False
            sign_ins[self.class_name] = self
            self.reply = f"”{self.class_name}“班级成功设置班级签到，班级成员共{self.users.shape[0]}人"
        else:
            # 签到已经存在
            self.reply = Message(f"{self.class_name}已添加签到，是否重置签到(是/否)！！")
            self.existence = True

    def reset_sign_in(self):
        """重新设置签到"""
        self.add_sign_in()
        self.reply = f"成功重置”{self.class_name}“签到。"

    def del_sign_in(self):
        """删除签到"""
        sign_ins.pop(self.class_name)

    async def __aenter__(self):
        """寻找出班级所有成员"""
        await mysql.execute(f"select 姓名, qq from {config.user_table} where 班级=%s", [self.class_name])
        self.users: DataFrame = mysql.form()
        self.add_sign_in()
        return self

    def text(self) -> Message:
        return Message(self.reply)

    async def __aexit__(self, *args):
        ...


class SignIn:
    def __init__(self,
                 user_id: int,
                 user_name: str,
                 class_name: str,
                 key: str,
                 typeof: str):
        self.class_name = class_name
        self.user_name = user_name
        self.user_id = user_id
        self.reply = ""
        self.key = key
        self.typeof = typeof

    def is_key(self):
        return self.sign_class.key == self.key

    def __enter__(self):
        # 签到的班级
        self.sign_class: SetSignIn = sign_ins.get(self.class_name)
        if self.sign_class:
            if self.sign_class.typeof == "any" or self.sign_class.typeof == self.typeof:
                if self.is_key():
                    self.start_sign()
                else:
                    self.reply = "关键字输入错误！！！"
            else:
                self.reply = "签到失败，您不该在这里签到！"
        else:
            self.reply = "您的班级未发起签到！！！"
        return self

    def start_sign(self):
        """
        开始签到
        查询该用户在班级群内(sign_class.users)并且用户不在已到内(sign_users)
            不在sign_users就进行添加，作为签到成功
        """
        user = (reset_index(self.sign_class.users[self.sign_class.users.qq == self.user_id]).loc[0])
        if user.shape[0] and self.user_id not in self.sign_class.sign_users:
            self.sign_class.sign_users.append(self.user_id)
            self.reply = f"”{user['姓名']}“签到成功"
        else:
            self.reply = "您已经签到过了！"

    def text(self):
        return Message(self.reply)

    def __exit__(self, *args):
        ...


class QuerySignIn:
    def __init__(self, class_name: str):
        self.class_name = class_name
        self.not_sign_user: DataFrame = DataFrame()
        self.reply = ""

    def __enter__(self):
        self.sign_class: SetSignIn = sign_ins.get(self.class_name)
        if self.sign_class:
            # 已签到用户
            self.sign_user = (self.sign_class.users[self.sign_class.users["qq"].isin(self.sign_class.sign_users)]
                              .reset_index().drop("index", axis=1))
            # 未签到用户
            self.not_sign_user = reset_index(concat([self.sign_class.users, self.sign_user])
                                             .drop_duplicates(keep=False))
        else:
            self.reply = f"{self.class_name}并未发起签到！！！"
        return self

    def text(self):
        if self.sign_class:
            yield Message("已签到\n" + " ".join(list(self.sign_user["姓名"])))
            yield Message("未签到\n" + " ".join(list(self.not_sign_user["姓名"])))
        else:
            yield Message("未发起签到！！！")

    def __exit__(self, *args):
        ...
