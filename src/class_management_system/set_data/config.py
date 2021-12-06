from pydantic import BaseSettings


class Config(BaseSettings):
    faculty = "faculty_table"
    expertise = "expertise_table"
    teacher = "teacher"
    class_table = "class_table"
