from pydantic import BaseSettings


class Config(BaseSettings):
    user_table = "user_info"
    user_table_param_not_null = {
        "姓名": str,
        "序号": int,
        "学号": int,
        "性别": str,
        "联系方式": int
    }
    user_table_param_type = {
        "序号": int,
        "姓名": str,
        "班级": str,
        "学号": int,
        "性别": str,
        "联系方式": int,
        "身份证号": str,
        "出生日期": str,
        "寝室": str,
        "寝室长": str,
        "微信": str,
        "QQ": int,
        "邮箱": str,
        "民族": str,
        "籍贯": str,
        "职位": str,
        "团员": str,
        "入党积极分子": str,
        "团学": str,
        "社团": str,
        "分数": int
    }
