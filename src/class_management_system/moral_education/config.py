from pydantic import BaseSettings


class Config(BaseSettings):
    score_log = "score_log"
    user_table = "user_info"
