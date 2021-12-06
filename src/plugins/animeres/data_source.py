from typing import Any, List, Tuple
from aiohttp import ClientSession, ClientTimeout
from feedparser import parse
from pydantic import BaseSettings


class AnimeRes(BaseSettings):
    def __init__(self, value: dict, **values: Any):
        super().__init__(**values)
        self.title = value['title']
        try:
            self.href = value["links"][1]['href'].split("&")[0]
        except KeyError:
            self.href = None
        self.tags = [i["term"] for i in value["tags"]]
        self.tag = value["tags"][0]['term']

    class Config:
        extra = "allow"


class GetDMHY:
    main_url = "https://dmhy.anoneko.com/topics/rss/rss.xml"

    def __init__(self, keyword: str):
        self.params = {"keyword": keyword}

    def classification(self) -> Tuple[dict, list]:
        values, tags = {}, []
        for i in self.resources:
            if i.href:
                if values.get(i.tag):
                    values[i.tag].append(i)
                else:
                    values[i.tag] = [i]
                    tags.append(i.tag)
        return values, tags

    def __getitem__(self, item: str) -> List[AnimeRes]:
        return self.values.get(item)

    def __iter__(self):
        return iter(self.tags)

    async def get(self) -> List[AnimeRes]:
        async with self.session.get(self.main_url, params=self.params) as res:
            return [AnimeRes(i) for i in parse(await res.text()).get("entries")]

    def __bool__(self):
        return bool(self.tags)

    async def __aenter__(self):
        self.session = ClientSession(timeout=ClientTimeout(600))
        self.resources = await self.get()
        self.values, self.tags = self.classification()
        self.length = len(self.tags)
        return self

    async def __aexit__(self, *args):
        await self.session.close()
