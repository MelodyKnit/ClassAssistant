from typing import Union, List, Tuple, Iterator, Any
from zipfile import ZipFile, ZIP_DEFLATED

from aiohttp import ClientSession, ClientTimeout
from nonebot import require
from pandas import DataFrame, Series
from os import path

task = "receiving"
task_file = "receiving_pictures"
mysql = require("botdb").MySQLdbMethods()
readfile = require("readfile").ReadFile("data", "class_system")


class Image:
    def __init__(self, data):
        self.name = data.get("file").split(".")[0]
        self.url = data.get("url")


class SaveImage:
    def __init__(self, class_name: str, file_name: str = None):
        self.class_name = class_name
        self.image_path = path.join(class_name, "images", "tasks_file")
        self.file_name = file_name

    def join(self, img: Union[Image, str]) -> str:
        return path.join(readfile.path, self.image_path, f"{img if isinstance(img, str) else img.name}.jpg")

    def for_in_name(self, images: List[Union[Image, str]]) -> Iterator[str]:
        for img in images:
            yield self.join(img)

    async def save(self, images: List[Image]):
        for img in images:
            async with self.session.get(img.url) as res:
                await readfile.write(
                    path.join(self.image_path, f"{self.file_name or img.name}.jpg"),
                    await res.read(), mode="wb")

    def remove(self, image: Union[str, Image]):
        readfile.remove(
            self.image_path,
            f"{image if isinstance(image, str) else image.name}.jpg"
        )

    async def __aenter__(self):
        self.session = ClientSession(timeout=ClientTimeout(total=10 * 60))
        return self

    async def __aexit__(self, *args):
        await self.session.close()


# 查询任务
class SelectTasks:
    def __init__(self, class_name: str, index: int = None):
        self.class_name = class_name
        self.index = index
        self.index_err = False

    def __await__(self):
        return self._init().__await__()

    async def get_tasks(self) -> DataFrame:
        """获取所有任务"""
        await mysql.execute(f"select * from {task} where class_name=%s", [self.class_name])
        return mysql.form()

    async def select_user_in_task(self, series: Union[Series, int]) -> DataFrame:
        """选择某项任务，列出所有提交任务的用户"""
        if isinstance(series, int):
            series = self[series]
        await mysql.execute(f"select * from {task_file} where create_time=%s and class_name=%s and title=%s",
                            [str(series["create_time"]), self.class_name, series["title"]])
        return mysql.form()

    async def select_user_not_in_task(self, users: Union[list, set]) -> DataFrame:
        await mysql.execute(f"select * from user_info where 班级=%s and qq not in({','.join(['%s'] * len(users))})",
                            [self.class_name, *users])
        return mysql.form()

    async def set_task(self, index: int = None) -> List[DataFrame]:
        """设置task的已经提交人数，并且返回索引值对应的用户，如果索引值为空则返回所有，超出则不返回"""
        task_user: List[DataFrame] = [await self.select_user_in_task(series) for i, series in self
                                      if i == index or index is None]

        if index is None:
            self.tasks['completed'] = [f"(提交{i.shape[0]}人)" for i in task_user]
        elif index in self:
            self.tasks.loc[index, 'completed'] = f"(提交{task_user[0].shape[0]}人)"
        else:
            self.index_err = True
        return task_user

    async def _init(self):
        self.tasks: DataFrame = await self.get_tasks()
        self.length = self.tasks.shape[0]
        self.task_user = await self.set_task(self.index)
        return self

    @staticmethod
    def submitted(user: DataFrame) -> str:
        if user.shape[0]:
            return "已提交\n" + ("\n".join([f"{v['user_name']} | {str(v['push_time']).split('.')[0]}"
                                         for i, v in user.iterrows()]))
        else:
            return "咦，文件呢？怎么还没人提交呀！"

    @staticmethod
    def not_submitted(user: DataFrame) -> str:
        if user.shape[0]:
            return "未提交\n" + (" ".join(user['姓名']))
        return "咦，所有人都交了哎!"

    async def text_one(self):
        """只回复一条消息"""
        return await self.text().__anext__()

    async def text(self):
        if self.index_err:
            yield f"咦，我怎么不知道有{self.index + 1}号？？？"
        else:
            if self.length:
                if self.index is None:
                    yield "\n".join(
                        [f"{i + 1}.{v['title']}{v['completed']} \n   "
                         f"发起时间：{v['create_time'].date()}" for i, v in self])
                else:
                    yield self.submitted(self.task_user[0])
                    user = await self.select_user_not_in_task(list(self.task_user[0]["user_id"]))
                    yield self.not_submitted(user)
            else:
                yield "干什么呀！你们班还没添加任务呢！"

    def __str__(self):
        return self.text()

    def __iter__(self) -> Iterator[Tuple[Any, Series]]:
        return iter(self.tasks.iterrows())

    def __getitem__(self, item: int) -> Union[Series, None]:
        if 0 <= item < self.length:
            return self.tasks.loc[item]
        return None

    def __contains__(self, index: int):
        return index is not None and 0 <= index < self.length

    def __bool__(self):
        return not (not self.length or self.index_err)


# 添加任务
class AddTask(SelectTasks):
    def __init__(self, title: str, user_id: int, class_name: str, jop: str):
        super().__init__(class_name)
        self.jop = jop  # 发起人所担任职务
        self.title = title  # 发起的标题
        self.user_id = user_id  # 发起人的id
        self.class_name = class_name  # 发起的班级

    async def repeat_task(self, tasks: DataFrame = None):
        """
        查询是否为重复任务
            重复任务返回False
            不是重复任务返回True
        """
        if not tasks:
            tasks = await self.get_tasks()
        return self.title not in list(tasks["title"])

    async def add_task(self):
        """创建一个文件收取的任务"""
        await mysql.execute_commit(f"insert into {task} (title,initiate,type,class_name) value (%s,%s,%s,%s)",
                                   [self.title, self.user_id, "image", self.class_name])

    async def __aenter__(self):
        if await self.repeat_task():
            await self.add_task()
            return f"“{self.title}”创建成功 ^_^"
        return "歪，你有个还有一个一模一样的任务呢！能不能先删掉那个重复的 >_<!!"

    async def __aexit__(self, *args):
        ...


# 提交任务
class PushTaskFile(SelectTasks):
    def __call__(self, user_name: str, user_id: int, index: int):
        self.user_name = user_name
        self.user_id = user_id
        self.index = index
        return self

    def is_exists(self) -> Union[bool, str]:
        """用户是否提交过"""
        task_user = self.task_user[0] if len(self.task_user) == 1 else self.task_user[self.index]
        user_id = list(task_user["user_id"])
        if self.user_id in user_id:
            return task_user["file_name"][user_id.index(self.user_id)]
        return False

    @staticmethod
    async def file_exists(image: Image) -> bool:
        """文件是否已存在"""
        await mysql.execute(f"select file_name from {task_file} where file_name=%s", [image.name])
        return bool(list(mysql.form()["file_name"]))

    async def insert(self, file_name: str, index: int = None):
        _task = self[index or self.index]
        await mysql.execute_commit(f"insert into {task_file} (title,user_id,user_name,class_name,file_name,create_time)"
                                   "value (%s,%s,%s,%s,%s,%s)",
                                   [_task['title'], self.user_id, self.user_name,
                                    self.class_name, file_name, str(_task['create_time']).split(".")[0]])

    async def delete(self, index: int = None):
        index = index or self.index
        await mysql.execute_commit(f"delete from {task_file} where class_name=%s and title=%s and user_id=%s",
                                   [self.class_name, self[index]['title'], self.user_id])

    async def save(self, image: Image):
        async with SaveImage(self.class_name) as res:
            file = self.is_exists()
            if file:
                res.remove(file)
                await self.delete()
            await res.save([image])
            await self.insert(image.name)
        return "提交成功！ ^_^"


# 导出任务
class ExportTask(SelectTasks):
    def __call__(self, index: int):
        """
        :参数 index:
            任务序号
        :返回: ExportTask
        """
        self.index = index
        self.task_user = self.task_user[0] if len(self.task_user) == 1 else self.task_user[index]
        return self

    def zip(self) -> Tuple[str, str]:
        """
        :说明:
            将文件打包成压缩文件保存到本地
        :返回:
            文件路径 文件名称
        """
        file = SaveImage(self.class_name)
        file_name = f"{self.class_name}{self[self.index]['title']}.zip"
        file_path = path.join(readfile.path, self.class_name, file_name)
        with ZipFile(file_path, "w", ZIP_DEFLATED) as zip_file:
            for i, img in self.task_user.iterrows():
                # 文件名以用户名称+qq组成
                zip_file.write(file.join(img["file_name"]), f"{img['user_name']}{img['user_id']}.jpg")
        return file_path, file_name


# 删除任务
class DeleteTask(SelectTasks):
    def __call__(self, index: int):
        """
        :参数 index:
            任务序号
        :返回: DeleteTask
        """
        self.index = index
        self.task_user = self.task_user[0] if len(self.task_user) == 1 else self.task_user[index]
        return self

    async def delete_table(self) -> str:
        """
        :说明:
            删除数据表，先删除文件表在删除任务表
        :返回:
            表格标题
        """
        title = self[self.index]["title"]
        await mysql.execute_commit(f"delete from {task_file} where class_name=%s and title=%s",
                                   [self.class_name, title])
        await mysql.execute_commit(f"delete from {task} where class_name=%s and title=%s",
                                   [self.class_name, title])
        return title

    def delete_file(self):
        """
        :说明:
            删除任务文件
        """
        file = SaveImage(self.class_name)
        for i, img in self.task_user.iterrows():
            file.remove(img["file_name"])

    async def delete(self):
        """
        :说明:
            先删除文件然后删除表格
        :返回:
            回复消息
        """
        self.delete_file()
        title = await self.delete_table()
        return f"“{title}”删除成功！"

