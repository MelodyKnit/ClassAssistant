from pydantic import BaseSettings


class Config(BaseSettings):
    user_table = "user_info"
    teacher_table = "teacher"
    class_table = "class_table"
