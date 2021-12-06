from nonebot import on_command
from nonebot.adapters.cqhttp import Bot, MessageEvent
from aiohttp import ClientSession, ClientConnectionError

cmd = on_command("bot")
host = None
port = 78
is_run = False


class JetBot:
    def __init__(self, command: str = None, typeof="move"):
        self.cmd = command
        self.typeof = typeof
        self.reply = ""

    async def __aenter__(self):
        self.session = ClientSession()
        return self

    async def get(self):
        global is_run
        try:
            async with self.session.get(f"http://{host}:{port}/login"):
                is_run = True
                return f"{host}连接成功！"
        except ClientConnectionError:
            is_run = False
            return f"{host}未发现jetbot，连接失败！！！"

    async def post(self):
        global is_run
        try:
            async with self.session.post(f"http://{host}:{port}/move", params={
                "cmd": self.cmd
            }) as res:
                if (await res.text()) == "false":
                    return "无该命令！"
        except ClientConnectionError:
            is_run = False
            return f"{host}未发现jetbot，连接失败！！！"

    async def __aexit__(self, *args):
        await self.session.close()


@cmd.handle()
async def cmd_(bot: Bot, event: MessageEvent):
    text = event.get_plaintext()
    if text:
        async with JetBot(text) as res:
            if "login" in text:
                global host
                host = text.split()[-1]
                await cmd.finish(await res.get())
            else:
                if is_run:
                    rep = await res.post()
                    if rep:
                        await cmd.finish(rep)
                else:
                    await cmd.finish("未与机器人建立连接")
