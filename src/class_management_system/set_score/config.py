from pydantic import BaseSettings


class Config(BaseSettings):
    user_table = "user_info"
    score = ["学习委员"]
