from pydantic import BaseSettings


class Config(BaseSettings):
    user_table = "user_info"
    class_table = "class_table"
    notification_time = 0
