from nonebot import require
from nonebot.adapters.cqhttp import Message
from pandas import DataFrame
from .config import Config

MySQLdbMethods = require("botdb").MySQLdbMethods
tools = require("tools")
get_url = tools.get_url
GetDocsSheet = tools.GetDocsSheet
mysql = MySQLdbMethods()
config = Config()


class AddGoods:
    """添加商品"""
    def __init__(self, user_id: int, url: str):
        self.url = url
        self.user_id = user_id
        self.reply = ""

    async def get_sheet(self) -> DataFrame:
        async with GetDocsSheet(self.url) as res:
            return res.data

    def text(self):
        return Message(self.reply)

    async def delete_goods(self):
        """删除原本的所有商品"""
        await mysql.execute_commit(f"delete from {config.shop_table} where teacher=%s",
                                   [self.user_id])

    async def __aenter__(self):
        """
        获取后删除商品然后写入新商品
        """
        self.data = await self.get_sheet()
        await self.delete_goods()
        if self.data.shape[0]:
            for k, v in self.data.iterrows():
                await self.insert(v["奖励"], v["分数"])
            self.reply = "商品更新完成。"
        else:
            self.reply = "商品已全部清空！！！"
        return self

    async def insert(self, name: str, price: int):
        """写入商品"""
        await mysql.execute_commit(f"insert into {config.shop_table} value (%s,%s,%s)",
                                   [self.user_id, name, price])

    async def __aexit__(self, *args):
        ...


class SelectGoods:
    """查询商品"""
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.reply = ""

    async def __aenter__(self):
        self.data = await self.select_goods()
        if self.data.shape[0]:
            self.reply = "商品列表："
            for k, v in self.data.iterrows():
                self.reply += f"\n{v['shop_name']} | {v['shop_price']}分"
        else:
            self.reply = "抱歉，未发现上架可以兑换商品！！！"
        return self

    async def select_goods(self) -> DataFrame:
        """
        依照用户的id与班级参数查询相关教师，在查找教师所上架的商品
        """
        await mysql.execute("SELECT shop_name,shop_price FROM class_table,user_info,shop where user_info.qq=%s and "
                            "user_info.班级=class_table.class_name and class_table.class_teacher=shop.teacher",
                            self.user_id)
        return mysql.form()

    def text(self):
        return Message(self.reply)

    async def __aexit__(self, *args):
        ...


class Purchase:
    def __init__(self, user_id: int, goods: list):
        self.user_id = user_id
        self.goods = goods
        self.goods_index = []
        self.goods_name = []
