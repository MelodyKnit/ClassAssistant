from nonebot import require
from typing import List, Union
from .config import Config
from aiohttp import ClientSession
from zipfile import ZipFile, ZIP_DEFLATED
from pandas import DataFrame, Series
from json import loads, dumps
from os import path
from datetime import datetime
from nonebot.adapters.cqhttp import Message, MessageSegment

config = Config()
mysql = require("botdb").MySQLdbMethods()
readfile = require("readfile").ReadFile("data", "class_system")


def select_names(names, typeof="name"):
    """查看是否有需要查找的用户的名字"""
    return f" and {typeof} in({','.join(['%s'] * len(names))})" if names else ""


class Image:
    def __init__(self, data):
        self.name = data.get("file").split(".")[0]
        self.url = data.get("url")


class GetMessage:
    def __init__(self, message: Message):
        self.text = ""
        self.images: List[Image] = []
        for msg in message:
            if msg.type == "text":
                txt = msg.data.get("text").strip()
                if txt:
                    self.text = txt
            elif msg.type == "image":
                self.images.append(Image(msg.data))


class AddScoreLog:
    def __init__(self, class_name: str,
                 name: Union[str, list],
                 user_id: Union[int, list],
                 student_id: Union[str, list],
                 images: List[Image],
                 explain_reason: str):
        self.class_name = class_name
        self.name = name
        self.image = images[0]
        self.user_id = user_id
        self.student_id = int(student_id)
        self.explain_reason = explain_reason
        self.reply = ""
        self.image_path = path.join(self.class_name, "images")
        self.prove_file = path.join(self.class_name, "prove.json")

    async def read_prove(self):
        """读取证明"""
        try:
            return loads(await readfile.read(self.prove_file))
        except FileNotFoundError:
            """读取失败时候创建新证明"""
            prove = {"all_file": [], "user_file": {}}
            readfile.mkdir(self.class_name)
            await readfile.write(self.prove_file, dumps(prove))
            return prove

    async def save_prove(self):
        """保存证明"""
        await readfile.write(self.prove_file, dumps(self.prove))

    async def query_user(self) -> DataFrame:
        """按照班级查找用户"""
        await mysql.execute(f"select 姓名, qq, 学号 from {config.user_table} where 班级=%s{select_names(self.name, '姓名')}",
                            [self.class_name, *self.name])
        return mysql.form()

    async def add_logger(self, name, user_id, student_id):
        await mysql.execute_commit(f"insert into {config.score_log} "
                                   "(class_name, name, qq, student_id, explain_reason, prove) value (%s,%s,%s,%s,%s,%s)",
                                   [self.class_name, name, user_id, student_id, self.explain_reason, self.image.name])

    async def save_image(self):
        """将图片保存到本地"""
        readfile.mkdir(self.image_path)
        if self.image.name not in self.prove["all_file"]:
            self.prove["all_file"].append(self.image.name)
            async with ClientSession() as session:
                async with session.get(self.image.url) as res:
                    data = await res.read()
                    await readfile.write(path.join(self.image_path, f"{self.image.name}.jpg"), data, mode="wb")

    async def __aenter__(self):
        self.prove = await self.read_prove()
        if isinstance(self.name, list):
            self.user_info = await self.query_user()
            for i, user in self.user_info.iterrows():
                self.reply += user["姓名"] + ","
                await self.add_logger(user["姓名"], user["qq"], user["学号"])
        else:
            await self.add_logger(self.name, self.user_id, self.student_id)
        self.reply += "德育日志添加成功！！"
        return self

    def text(self):
        return Message(self.reply)

    async def __aexit__(self, *args):
        await self.save_image()
        await self.save_prove()


class SaveDialog:
    def __init__(self, class_name: str, names: list):
        self.date = datetime.now()
        self.class_name = class_name
        self.names = names
        self.class_file = path.join(readfile.path, class_name)  # 班级文件路径
        self.not_value = True                                   # 是否为空数据
        self.file_path = ""
        self.reply = ""

    def save(self):
        """保存到本地文件"""
        try:
            self.data.to_excel(self.file_path, index=False)
        except FileNotFoundError:
            readfile.mkdir(self.class_name)
            self.save()

    def file_name(self, suffix: str):
        """根据班级名+时间保存为文件名"""
        if self.names:
            file_name = '_'.join(set(self.data["姓名"]))
        else:
            file_name = self.class_name
        date = str(self.date).split(".")[0].replace(" ", "-").replace(":", "-")
        return file_name + date + "." + suffix

    @staticmethod
    def set_data(data: DataFrame) -> DataFrame:
        """设置数据，将说明与时间相结合，并且添加附加分名称与分数"""
        data["说明"] = [str(data.loc[i]["log_time"].date()) + data.loc[i]["说明"] for i in range(data.shape[0])]
        data["附加分名称"], data["分数"] = "", ""
        data.drop(columns="log_time", axis=0, inplace=True)
        data.sort_values(by="姓名", ascending=False, inplace=True)        # 按照姓名排序
        return data[["学号", "姓名", "附加分名称", "分数", "说明"]]

    async def get_data(self) -> DataFrame:
        """查找用户，并且按照当月筛选出用户"""
        await mysql.execute(
            f"select student_id 学号, name 姓名, explain_reason 说明, log_time, prove from {config.score_log} "
            f"where year(log_time)=%s and month(log_time)=%s and class_name=%s{select_names(self.names)}",
            [self.date.year, self.date.month, self.class_name, *self.names])
        return mysql.form()

    async def __aenter__(self):
        data: DataFrame = await self.get_data()
        if data.shape[0]:
            self.not_value = False
            self.data: DataFrame = self.set_data(data)
            self.name = self.file_name("xlsx")         # 文件名
            self.file_path = path.join(self.class_file, self.name)
            self.save()
        else:
            self.reply = "未发现日志！！！"
        return self

    def text(self):
        return Message(self.reply)

    async def __aexit__(self, *args):
        ...


class ExportProve(SaveDialog):
    def __init__(self, class_name: str, names: list):
        super().__init__(class_name, names)

    async def __aenter__(self):
        self.data: DataFrame = await self.get_data()
        if self.data.shape[0]:
            self.not_value = False
            self.name = self.file_name("zip")  # 文件名
            self.file_path = path.join(self.class_file, self.name)
            self.zip()
        else:
            self.reply = "未发现日志！！！"
        return self

    def zip(self):
        prove = set(self.data["prove"])
        length = len(prove)
        yield "开始进行打包..."
        with ZipFile(self.file_path, "w", ZIP_DEFLATED) as zip_file:
            for img in prove:
                try:
                    zip_file.write(path.join(self.class_file, "images", f"{img}.jpg"), f"{img}.jpg")
                except FileNotFoundError as err:
                    length -= 1
                    print(err)
        yield f"打包完成\n文件数量：{length}\n开始发送请耐心等待..."
