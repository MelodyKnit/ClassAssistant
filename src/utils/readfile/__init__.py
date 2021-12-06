from aiofile import async_open
from nonebot import export
from os.path import join, dirname
import os

export = export()

global_default_path: str = os.getcwd()


def set_path(path):
    """设置读取的文件路径"""
    global global_default_path
    global_default_path = path


class ReadFile:
    # 默认路径
    default_path: str = global_default_path

    def __init__(self, *args: str):
        """
        :param args: 默认路径下的其它文件
        """
        self.path = join(self.default_path, *args)

    async def read(self, file_name, *, mode="r"):
        async with async_open(join(self.path, file_name), mode=mode) as file:
            return await file.read()

    async def write(self, file_name, data, *, mode="w", end=True):
        try:
            async with async_open(join(self.path, file_name), mode=mode) as file:
                return await file.write(data)
        except FileNotFoundError as err:
            if end:
                self.mkdir(dirname(file_name))
                await self.write(file_name, data, mode=mode, end=False)
            else:
                raise err

    def listdir(self, *args: str) -> list:
        return os.listdir(join(self.path, *args))

    def remove(self, *args: str) -> bool:
        try:
            os.remove(join(self.path, *args))
            return True
        except FileNotFoundError:
            return False

    def mkdir(self, *args: str) -> bool:
        try:
            os.makedirs(join(self.path, *args))
            return True
        except FileExistsError:
            return False


# 设置读取的文件路径
export.set_path = set_path
export.ReadFile = ReadFile

