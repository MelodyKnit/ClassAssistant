from pydantic import BaseSettings


class Config(BaseSettings):
    shop_table = "shop"
