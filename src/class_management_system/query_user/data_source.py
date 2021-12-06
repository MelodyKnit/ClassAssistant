from nonebot import require
from nonebot.adapters.cqhttp import Message, MessageSegment
from .config import Config
from pandas import Series, DataFrame

config = Config()
mysql = require("botdb").MySQLdbMethods()


class Query:
    def __init__(self, param: list, group_id: int):
        self.group_id = group_id
        self.param = param
        self.index = []
        self.user_name = []
        self.uid = []

    def _split(self):
        for i in self.param:  # type: str
            if i.isdigit():
                if len(i) < 4:
                    self.index.append(int(i))
                else:
                    self.uid.append(int(i))
            else:
                self.user_name.append(i)

    @staticmethod
    def _fmt_in(tag: str, al: list):
        if al:
            return f"{tag} in({','.join(['%s'] * len(al))})"

    def _where(self, is_user: bool = True):
        fmt = []
        if is_user:
            for i in [self._fmt_in("qq", self.uid),
                      self._fmt_in("学号", self.uid),
                      self._fmt_in("序号", self.index),
                      self._fmt_in("姓名", self.user_name)]:
                if i:
                    fmt.append(i)
        else:
            for i in [self._fmt_in("qq", self.uid),
                      self._fmt_in("telephone", self.uid),
                      self._fmt_in("name", self.user_name)]:
                if i:
                    fmt.append(i)
        return " or ".join(fmt)

    async def __aexit__(self, *args):
        ...


class QueryUser(Query):
    def __init__(self, param: list, group_id: int):
        super().__init__(param, group_id)
        self.not_user = True
        self.is_err = False
        self.reply = Message()
        self._split()

    async def _get_class_name(self):
        """获取班级名称，并且查询是否为班级群，不是班级群则报错KeyError"""
        await mysql.execute(f"select class_group, class_name from {config.class_table}")
        df: DataFrame = mysql.form()
        class_group = list(df['class_group'])
        if self.group_id in class_group:
            return "and 班级='%s'" % df["class_name"][class_group.index(self.group_id)]
        raise KeyError

    async def get_user(self):
        """获取用户，是否有该用户，如果有则对信息进行提取并筛选出需要展示的信息"""
        try:
            await mysql.execute(f"select * from {config.user_table} where ({self._where()}) {await self._get_class_name()}",
                                [*(self.uid * 2), *self.index, *self.user_name])
            data: DataFrame = mysql.form()
            length = data.shape[0]          # 提取的用户数量
            if length < 1:
                self.reply.append("抱歉，未查询到该用户！！！")
                self.not_user = True
            elif length == 1:
                self.user(data.loc[0])
                self.not_user = False
            else:
                self.users(data)
                self.not_user = False
        except KeyError:
            self.is_err = True
            self.reply = "此群并非班级群，无法使用查询！！！"

    async def get_teacher(self):
        """获取教师"""
        await mysql.execute(f"select * from {config.teacher_table} where ({self._where(False)})",
                            [*(self.uid * 2), *self.user_name])
        data: DataFrame = mysql.form()
        length = data.shape[0]
        teachers = []
        if length:
            teachers.append("查询到为教师：")
            for i in range(length):
                teacher = data.loc[i]
                teachers.append(f"姓名：{teacher['name']}\n"
                                f"QQ：{teacher['qq']}\n"
                                f"联系方式：{teacher['telephone']}")
            self.reply = Message('\n-----\n'.join(teachers))

    @staticmethod
    def user_key(user: Series, auto_end: str = "\n"):
        """从用户key中查看是否存在值，如果存在则返回该数据加key"""
        def _(key, end: str = auto_end):
            """
            :param key: 数据的key
            :param end: 在结尾追加字符
            """
            value = user.get(key)
            if value != "None" and value != "":
                return f"{key}：{value}{end}"
            return ""
        return _

    def user(self, user: Series):
        info = self.user_key(user)
        birthday, dorm = [""] * 2
        if user.get("出生日期"):
            birthday = user["出生日期"].date()
        if user.get("寝室长"):
            if user['寝室长'] == '是':
                dorm = f"{user['寝室']}（寝室长）"
            else:
                dorm = user["寝室"]
        self.reply.append(f"{info('序号')}"
                          f"{info('姓名')}"
                          f"{info('性别')}"
                          f"{info('班级')}"
                          f"{info('社团')}"
                          f"{info('团学')}"
                          f"{info('团员')}"
                          f"{info('入党积极份子')}"
                          f"{info('民族')}"
                          f"寝室：{dorm}\n"
                          f"出生日期：{birthday}\n"
                          f"{info('学号')}"
                          f"{info('微信')}"
                          f"{info('联系方式')}"
                          f"{info('邮箱')}"
                          f"{info('分数', '')}")

    def users(self, users: DataFrame):
        for i in range(users.shape[0]):
            user = users.loc[i]
            self.user(user)
            if i < users.shape[0] - 1:
                self.reply.append("\n-----\n")

    def text(self):
        return self.reply

    async def __aenter__(self):
        """
        查找用户，查看是否有用户，并且没有出现报错，如果没有报错并且没有用户则进行查找是否为教师
        """
        await self.get_user()
        if not self.is_err and self.not_user:
            await self.get_teacher()
        return self


class AtUser(Query):
    def __init__(self, param: list, group_id: int):
        super().__init__(param, group_id)
        self.not_user = True
        self.is_err = False
        self.users = []
        self.reply = Message()
        self._split()

    async def _get_class_name(self):
        """从数据库中检索出班级，提取班级名称，班级群号是唯一的"""
        await mysql.execute(f"select class_name from {config.class_table} where class_group=%s",
                            [self.group_id])
        self.class_name = mysql.form()["class_name"][0]

    async def get_user(self):
        await mysql.execute(f"select qq from {config.user_table} where ({self._where()}) and 班级=%s",
                            [*(self.uid * 2), *self.index, *self.user_name, self.class_name])
        self.users = mysql.form()["qq"]

    def text(self):
        for i in self.users:
            self.reply += MessageSegment.at(i)
        return self.reply

    async def __aenter__(self):
        try:
            await self._get_class_name()
            await self.get_user()
        except KeyError:
            self.is_err = True
        return self






