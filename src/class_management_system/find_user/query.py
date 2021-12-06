from nonebot import require
from nonebot.adapters.cqhttp import Message
from pandas import DataFrame, Series

mysql = require("botdb").MySQLdbMethods()


def get(data: Series):
    def _(key: str, fmt: str = None, is_str: str = "") -> str:
        """
        :param key: 关键字
        :param fmt: 替换字符
        :param is_str: 满足条件
        :return:
        """
        value = data.get(key)
        if value == is_str or " " != value != "None" and value:
            return fmt if fmt else f"{key}：{value}"
        return ""
    return _


def dataMap(data: DataFrame):
    def _(key, arg, na_action=None):
        values: Series = data.get(key)
        if values is not None:
            data[key] = values.map(arg, na_action)
    return _


class SplitUser:
    def __init__(self, message: Message = None):
        self.message = message
        self.index = []
        self.user_id = []
        self.name = []
        if message:
            for msg in message:
                if msg.type == "at":
                    self.user_id.append(msg.data.get("qq"))
                elif msg.type == "text":
                    for text in msg.data.get("text").split():
                        if text.isdigit():
                            if len(text) < 5:
                                self.index.append(int(text))
                            else:
                                self.user_id.append(int(text))
                        else:
                            self.name.append(text)

    def __bool__(self) -> bool:
        return bool(self.user_id or self.index or self.name)


class QueryUsers:
    exhibition = {
        "序号", "姓名", "班级", "学号", "性别", "联系方式", "出生日期", "寝室", "寝室长", "微信", "qq",
        "邮箱", "民族", "职位", "团员", "入党积极份子", "团学", "社团", "分数"
    }

    def __init__(self, class_name: str, screen: set = None):
        screen = screen or self.exhibition
        self.class_name = class_name
        self.screen = {"姓名", *screen} & self.exhibition

    def single_reply(self, users: Series) -> str:
        """单条回复信息"""
        find = get(users)
        return "\n".join([i for i in [find(v) for v in self.screen] if i])

    def multiple_replies(self, users: DataFrame) -> str:
        """多条回复信息"""
        return "\n- - - - -\n".join([self.single_reply(v) for i, v in users.iterrows()])

    async def teacher_reply(self, users: SplitUser) -> str:
        """查找到的教师回复词"""
        user = await self.query_teacher(users)
        length = user.shape[0]
        if length:
            return "\n- - - - -\n".join([f"姓名：{u['name']}\nQQ：{u['qq']}\n联系方式：{u['telephone']}"
                                         for i, u in user.iterrows()])
        else:
            return ""

    async def users_reply(self, users: SplitUser) -> str:
        """查找到的学生回复词"""
        user = await self.query_user(users)
        length = user.shape[0]
        if length == 1:
            return self.single_reply(user.loc[0])
        elif length > 1:
            return self.multiple_replies(user)
        else:
            return ""

    async def text(self, users: SplitUser = None):
        text = await self.users_reply(users)
        if text:
            return Message(text)
        text = await self.teacher_reply(users)
        if text:
            return Message("查询到为教师：\n- - - - -\n" + text)
        return Message("未查找到该用户！！")

    async def query_user(self, users: SplitUser) -> DataFrame:
        """查找班级某些用户"""
        await mysql.execute(f"""select {','.join(self.screen)} from user_info where 班级=%s and ({self.set_where(
            qq=users.user_id,
            学号=users.user_id,
            序号=users.index,
            姓名=users.name
        )})""", [self.class_name, *(users.user_id * 2), *users.index, *users.name])
        data: DataFrame = mysql.form()
        _map = dataMap(data)
        _map("出生日期", lambda x: str(x).split()[0])
        _map("寝室长", lambda x: "寝室长" if x == "是" else None)
        return data

    @classmethod
    async def query_teacher(cls, users: SplitUser) -> DataFrame:
        """查找教师"""
        await mysql.execute(f"""select * from teacher where {cls.set_where(
            qq=users.user_id,
            name=users.name,
        )}""", [*users.user_id, *users.name])
        return mysql.form()

    @staticmethod
    def in_method(tag: str, al: list):
        """sql的in方法"""
        if al:
            return f"{tag} in({','.join(['%s'] * len(al))})"

    @classmethod
    def set_where(cls, format_str: str = "or", **kwargs: list):
        """
        设置where条件
        :param format_str: 需要格式化的字符
        :param kwargs: 列名与包含的数据
        :return:
            如果有数据，例如 qq=[123456]
            返回 qq in(%s)
            如果有多个条件，例如 qq=[123456], name=[654897]
            返回 qq in(%s) or name in(%s)
        """
        return f" {format_str} ".join([cls.in_method(i, kwargs[i]) for i in kwargs if kwargs[i]])

    @staticmethod
    def split(message: Message = None) -> SplitUser:
        """拆分出用户，索引，号码"""
        return SplitUser(message)
