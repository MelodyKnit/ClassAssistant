from aiomysql import connect, Warning, Connection, Cursor, IntegrityError, InternalError, OperationalError, Error
from nonebot import get_driver
from warnings import filterwarnings
from nonebot.log import logger
from pandas import DataFrame

driver = get_driver()
filterwarnings("error", category=Warning)


class MySQLdbMethods:
    __slots__ = ("_conn", "cur", "description")
    cur: Cursor
    is_run = False                  # 数据库是否启动
    _conn: Connection
    config = {
        "db": driver.config.mysql_db,
        "host": driver.config.mysql_host,
        "user": driver.config.mysql_user,
        "password": str(driver.config.mysql_password),
    }

    async def execute(self, query: str, param: list = None, err_num: int = 5):
        try:
            await self.cur.execute(query, param)
        except (RuntimeError, InternalError) as err:
            if err_num:
                logger.warning("数据库连接超时，重新建立连接！")
                await self.close()
                await self.connect()
                await self.execute(query, param, err_num-1)
            else:
                print(query, param)
                raise err
        except IntegrityError:
            await self._conn.rollback()
            raise IntegrityError

    async def execute_commit(self, query: str, param: list = None):
        await self.execute(query, param)
        await self._conn.commit()

    def fetchall(self):
        return self.cur.fetchall()

    def form(self) -> DataFrame:
        """将表格数据转为DataFrame"""
        data = self.fetchall().result()
        return DataFrame({t[0]: [v[i] for v in data] for i, t in enumerate(self.cur.description)})

    @classmethod
    async def connect(cls):
        """与数据库建立连接"""
        cls._conn = await connect(**cls.config)
        cls.cur = await cls._conn.cursor()

    @classmethod
    async def close(cls):
        """关闭数据库"""
        try:
            await cls.cur.close()
            cls._conn.close()
        except Error as err:
            logger.error("数据库断开出现错误")
            logger.error(err)

    @classmethod
    async def start(cls):
        """开启数据库"""
        try:
            await cls.connect()
            logger.success("成功与MySQL数据库建立连接！")
        except AssertionError as err:
            logger.error(err)
        except OperationalError as err:
            logger.error("数据库连接失败！请检查配置文件是否输入有误！")
            logger.error(err)
        else:
            cls.is_run = True

    @classmethod
    async def stop(cls):
        """停止数据库"""
        if cls.is_run:
            await cls.close()


driver.on_startup(MySQLdbMethods.start)
driver.on_shutdown(MySQLdbMethods.stop)
