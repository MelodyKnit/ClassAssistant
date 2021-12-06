from nonebot import require
from .config import Config
from nonebot.adapters.cqhttp import Message
from aiomysql import IntegrityError

ADD = "add"
DEL = "del"
MySQLdbMethods = require("botdb").MySQLdbMethods
mysql = MySQLdbMethods()
config = Config()


# 学院院系
class Faculty:
    def __init__(self,
                 typeof: str,
                 faculty: str,
                 invitee: int
                 ):
        """
        :param faculty: 需要添加的院系
        :param invitee: 添加人的QQ
        """
        self.typeof = typeof
        self.faculty = faculty      # 院系
        self.invitee = invitee      # 添加人
        self.is_err = False
        self.reply_text = None
        self.table_name = config.faculty

    async def __aenter__(self):
        try:
            if self.typeof == ADD:
                # ----- 添加数据 -----
                await mysql.execute_commit(
                    f"insert into {self.table_name} value (%s,%s)", param=[
                        self.faculty, self.invitee
                    ])
                # ----- 添加数据回复 -----
                self.reply_text = f"”{self.faculty}“添加成功。"
            elif self.typeof == DEL:
                # ----- 删除数据回复 -----
                await mysql.execute_commit(f"delete from {self.table_name} where faculty=%s", param=[
                    self.faculty])
                # ----- 删除成功回复 -----
                self.reply_text = f"“{self.faculty}”已删除。"
        except IntegrityError:
            if self.typeof == DEL:
                # ----- 删除失败回复 -----
                self.reply_text = f"“{self.faculty}”删除失败，可能”{self.faculty}“下还所在专业未删除！！！"
            elif self.typeof == ADD:
                # ----- 添加失败回复 -----
                self.reply_text = f"”{self.faculty}“已经添加，无需重复执行！！！"
            self.is_err = True
        return self

    def text(self) -> Message:
        return Message(self.reply_text)

    async def __aexit__(self, *args):
        ...


# 院系的专业
class Expertise:
    def __init__(self,
                 typeof,
                 expertise: str,
                 faculty: str = None
                 ):
        self.typeof = typeof
        self.faculty = faculty      # 院系
        self.expertise = expertise  # 专业
        self.is_err = False
        self.reply_text = None
        self.table_name = config.expertise

    async def __aenter__(self):
        try:
            if self.typeof == ADD:
                # ----- 添加数据 -----
                await mysql.execute_commit(
                    f"insert into {self.table_name} value (%s,%s)", param=[
                        self.faculty, self.expertise
                    ])
                # ----- 添加成功回复 -----
                self.reply_text = f"“{self.expertise}”添加成功，所在院系”{self.faculty}“。"
            elif self.typeof == DEL:
                # ----- 删除数据 -----
                await mysql.execute_commit(f"delete from {self.table_name} where expertise=%s", param=[
                    self.expertise])
                # ----- 删除成功回复 -----
                self.reply_text = f"“{self.expertise}”已删除。"
        except IntegrityError:
            if self.typeof == ADD:
                # ----- 添加失败回复 -----
                self.reply_text = f"”{self.expertise}“添加失败，可能是”{self.faculty}“不存在，或者是”{self.expertise}“已经添加过！！！"
            self.is_err = True
        return self

    def text(self) -> Message:
        return Message(self.reply_text)

    async def __aexit__(self, *args):
        ...


class Teacher:
    def __init__(self,
                 typeof: str,
                 name: str = None,
                 qq: int = None,
                 tel: int = None,
                 invitee: int = None
                 ):
        self.qq = qq                    # 教师QQ
        self.tel = tel                  # 教师电话
        self.name = name                # 教师姓名
        self.invitee = str(invitee)     # 添加人
        self.typeof = typeof
        self.is_err = False
        self.reply_text = None
        self.table_name = config.teacher

    async def __aenter__(self):
        try:
            if self.typeof == ADD:
                # ----- 添加教师信息 -----
                await mysql.execute_commit(f"insert into {self.table_name} values (%s,%s,%s,%s)", param=[
                    self.name, self.qq, self.invitee, self.tel
                ])
                # ----- 添加成功回复 -----
                self.reply_text = f"”{self.name}“添加成功。"
            elif self.typeof == DEL:
                # # ----- 删除教师信息 -----
                if self.name:
                    sql = f"delete from {self.table_name} where name=%s"
                else:
                    sql = f"delete from {self.table_name} where qq=%s"
                await mysql.execute_commit(sql, param=[self.name or self.qq])
                # # ----- 删除成功回复 -----
                self.reply_text = f"”{self.name or self.qq}“已删除。"
        except IntegrityError:
            if self.typeof == ADD:
                # ----- 添加失败回复 -----
                self.reply_text = f"“{self.name}”添加失败，可能重复添加某条数据，或者缺少某些数据！！！"
            elif self.typeof == DEL:
                # ----- 删除失败回复 -----
                self.reply_text = f"“{self.name}”删除失败，可能“{self.name}”下还有班级未删除！！！"
        return self

    def text(self):
        return Message(self.reply_text)

    async def __aexit__(self, *args):
        ...


class Class:
    def __init__(self,
                 typeof: str,
                 class_name: str = None,
                 class_id: int = None,
                 class_group: int = None,
                 class_teacher: int = None,
                 expertise: str = None
                 ):
        self.typeof = typeof
        self.class_name = class_name                # 班级全称
        self.class_id = class_id                    # 班级id
        self.class_group = class_group              # 班级群
        self.class_teacher = class_teacher     # 班主任
        self.expertise = expertise                  # 专业
        self.is_err = False
        self.reply_text = None
        self.table_name = config.class_table

    async def __aenter__(self):
        try:
            if self.typeof == ADD:
                # ----- 添加班级 -----
                await mysql.execute_commit(f"insert into {self.table_name} values (%s,%s,%s,%s,%s)", param=[
                    self.class_id, self.expertise, self.class_group, self.class_name, self.class_teacher
                ])
                # ----- 添加成功回复 -----
                self.reply_text = f"”{self.class_name}“添加完成，您已成为”{self.class_name}“班主任，可以在此群导入班级表格。"
            elif self.typeof == DEL:
                # ----- 删除班级 -----
                if self.class_name:
                    sql = f"delete from {self.table_name} where class_name=%s"
                else:
                    sql = f"delete from {self.table_name} where class_group=%s"
                await mysql.execute_commit(sql, param=[self.class_name or self.class_group])
                # ----- 删除成功回复 -----
                self.reply_text = f"“{self.class_name or self.class_group}“已删除"
        except IntegrityError:
            if self.typeof == ADD:
                # ----- 添加失败回复 -----
                self.reply_text = f"“{self.class_name}”添加失败，错误原因可能如下：\n1.教师不在数据库中。\n2.此专业存在。\n3.此班级已创建！！！"
            elif self.typeof == DEL:
                # ----- 删除失败回复 -----
                self.reply_text = f"“{self.class_name}”删除失败，请先清空该班级下的学生信息！！！"
        return self

    def text(self):
        return Message(self.reply_text)

    async def __aexit__(self, *args):
        ...
